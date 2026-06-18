# sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/typhoon.c

Purpose: PCI Ethernet driver for the 3Com 3CR990/3C990 Typhoon family with an onboard 3XP processor. It owns PCI probe/remove, firmware loading, DMA ring setup, NAPI receive, transmit descriptor construction, ethtool link/WOL controls, statistics, suspend/resume, and sleep/runtime image transitions.

Important APIs, types, and functions: `struct typhoon` is the private runtime state and `struct typhoon_shared` is the coherent DMA region consumed by the NIC. Key paths are `typhoon_init_one()`, `typhoon_open()`, `typhoon_close()`, `typhoon_start_tx()`, `typhoon_poll()`, `typhoon_interrupt()`, `typhoon_start_runtime()`, `typhoon_stop_runtime()`, `typhoon_download_firmware()`, `typhoon_boot_3XP()`, `typhoon_issue_command()`, `typhoon_rx()`, and `typhoon_tx_timeout()`. `typhoon_ethtool_ops` exposes driver info, ring sizes, WOL, and link settings.

Control flow: probe enables PCI, selects MMIO or PIO, allocates coherent shared rings, resets the 3XP, boots the sleep image, reads the MAC and image version, then sleeps the adapter before registering the netdev. Open requests firmware, wakes the card, installs IRQ/NAPI, downloads and boots the runtime image, programs packet size, MAC, transceiver, VLAN type, offload tasks, RX filter, and enables TX/RX. Interrupts only schedule NAPI; NAPI drains responses, completions, RX rings, and refills the free-buffer ring.

State and persistence: durable device state is hardware/firmware state plus the cached firmware pointer. Runtime state includes byte-offset ring cursors, coherent DMA indexes, RX SKB/DMA slots, command-response wait state, link speed/duplex, selected transceiver, WOL flags, offload mask, and saved statistics used while the sleep image cannot report full stats.

Dependencies and integration points: depends on PCI, DMA mapping, request_firmware for `3com/typhoon.bin`, NAPI, VLAN offload, ethtool, PCI PM, and the descriptor/register ABI in `typhoon.h`. The device advertises SG, IPv4 checksum, TSO, TX VLAN, RX VLAN stripping, and RX checksum.

Risks: command responses are polled with long non-preemptible waits; missed response races are patched with a self-interrupt. TX DMA map failures are not explicitly checked. The driver assumes 32-bit DMA despite 64-bit-looking firmware fields. RX DMA cannot use the usual 2-byte alignment workaround. Sleep/runtime transitions rely on precise 3XP status values and firmware behavior. WAKE_MAGIC is warned as incompatible with always-on VLAN offload.

Test signals: successful firmware request/download, probe MAC read, runtime boot, TX/RX traffic with checksum/VLAN/TSO, NAPI completions without stuck interrupts, tx-timeout recovery, multicast/promiscuous filter changes, ethtool link mode changes, stats continuity across close/open, suspend/resume with WOL, and clean failure if firmware is missing or invalid.
