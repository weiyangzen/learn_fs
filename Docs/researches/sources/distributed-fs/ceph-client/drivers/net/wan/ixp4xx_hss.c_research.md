# sources/distributed-fs/ceph-client/drivers/net/wan/ixp4xx_hss.c

## Purpose
`ixp4xx_hss.c` is an Intel IXP4xx HSS synchronous serial/HDLC driver. It configures the platform NPE firmware, Queue Manager queues, GPIO modem-control lines, DMA descriptors, NAPI receive handling, and generic HDLC integration for IXP4xx HSS ports.

## Important APIs, Types, And Functions
`struct port` is the central device state: NPE handle, queue IDs, GPIOs, HDLC netdevice, NAPI object, DMA descriptor table, RX/TX buffer arrays, clock settings, carrier, and HDLC config flags. `struct msg` models NPE commands. `struct desc` models HDLC packet descriptors. Important functions include `hss_npe_send()`, `hss_config()`, `hss_load_firmware()`, `hss_hdlc_poll()`, `hss_hdlc_xmit()`, `request_hdlc_queues()`, `init_hdlc_queues()`, `hss_hdlc_open()`, `hss_hdlc_close()`, `hss_hdlc_attach()`, `find_best_clock()`, `hss_hdlc_ioctl()`, and `ixp4xx_hss_probe()`.

## Control Flow
Probe verifies SoC HDLC/HSS feature bits through syscon, requests an NPE engine from device tree, reads Queue Manager queue phandles, obtains CTS/RTS/DCD/DTR/internal-clock GPIOs, allocates an HDLC netdevice, sets hardware attach/xmit callbacks, adds NAPI, and registers the device. Open calls `hdlc_open()`, loads NPE firmware if needed, requests queues, allocates coherent descriptors and DMA RX buffers, samples DCD, requests a DCD IRQ, asserts DTR/RTS, populates TX-ready and RX-free queues, enables NAPI and queue IRQs, configures the NPE port, starts packet flow, and schedules receive polling. TX maps skb data, obtains a TX descriptor from the ready queue, submits it to the TX queue, and stops the netdev queue if descriptors run out. RX IRQ disables queue IRQ and schedules NAPI; polling drains descriptors, maps status to stats, copies/switches buffers depending on endian mode, calls `hdlc_type_trans()`, and returns descriptors to RX-free.

## State And Persistence
State is volatile and hardware-backed. `ports_open` and `dma_pool` are module-global. Per-port descriptor memory is coherent DMA. Queue contents live in IXP4xx Queue Manager hardware. Carrier is based on DCD unless loopback forces carrier. Close drains queues, disables IRQs, deasserts modem lines, frees DMA buffers/descriptors, releases queues, and calls `hdlc_close()`.

## Dependencies And Integration Points
The driver integrates with generic HDLC, IXP4xx NPE firmware loader, IXP4xx Queue Manager, syscon feature detection, device tree phandles, GPIO descriptors, DMA API, NAPI, and platform-driver probing.

## Risks
Probe contains a concrete lifecycle hazard: it assigns `ndev = alloc_hdlcdev(port)` and then separately assigns `port->netdev = alloc_hdlcdev(port)`, but initializes and registers `ndev` while runtime/remove paths use `port->netdev`. That can leak one netdevice and unregister/free the wrong one. Several NPE command failures call `BUG()`, turning firmware/queue faults into kernel panics. `hss_hdlc_ioctl()` calls `hss_hdlc_set_clock()` before fully validating `clock_type`, so an invalid value after GPIO side effects should be considered. Queue drain loops can log critical errors if NPE descriptors remain stuck.

## Test Signals
Tests need platform/device-tree coverage for all phandles, open/close queue allocation and cleanup, DCD IRQ carrier changes, internal/external clock ioctls, CRC16/CRC32 attach validation, TX descriptor exhaustion and wakeup, RX status-to-stats mapping, and remove after probe failure. Static analysis should flag the double-netdev allocation and mismatched `port->netdev` usage.
