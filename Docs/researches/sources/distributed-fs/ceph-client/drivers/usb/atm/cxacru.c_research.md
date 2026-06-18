# sources/distributed-fs/ceph-client/drivers/usb/atm/cxacru.c

## Purpose
`cxacru.c` is a `usbatm` mini-driver for Conexant AccessRunner USB ADSL modems. It handles modem-specific firmware loading, command-channel transfers, sysfs DSL status/configuration, MAC acquisition, line start/stop, and periodic status polling while delegating ATM cell I/O to the shared `usbatm` core.

## Important APIs, Types, And Functions
- `struct cxacru_data` stores the `usbatm` instance, modem type, ADSL status, card-info array, polling state, command URBs, command buffers, completions, and mutexes.
- `cxacru_bind()` allocates command buffers/URBs, validates command endpoints, initializes polling work, and sets `UDSL_SKIP_HEAVY_INIT` if firmware is already alive.
- `cxacru_heavy_init()` requests `cxacru-fw.bin` and optional `cxacru-bp.bin`, writes PLL/SDRAM/firmware/signature memory, starts firmware, clears halts, and verifies card status.
- `cxacru_cm()` serializes command-monitor packets over endpoint 1 and validates response command/status packets.
- `cxacru_atm_start()` fetches MAC address, starts the ADSL line, and starts polling.
- `cxacru_poll_status()` reads `CARD_INFO_GET`, updates `card_info`, logs line transitions, updates ATM signal, and reschedules delayed work.
- Sysfs attributes expose rates, margins, attenuation, errors, modulation, MAC, `adsl_state`, and write-only `adsl_config`.

## Control Flow
The USB driver filters out vendor-specific "USB NET CARD" routers, then calls `usbatm_usb_probe()` with `cxacru_driver`. Bind creates the mini-driver state and command URBs. If `cxacru_card_status()` succeeds, heavy init is skipped; otherwise the `usbatm` heavy-init thread loads firmware and then initializes ATM. ATM start fetches the MAC and sends `CHIP_ADSL_LINE_START`. Poll work periodically retrieves card info, updates sysfs-backed cached values, changes ATM carrier state, and reschedules until stopped or shutdown.

## State And Persistence Behavior
Runtime state includes the cached `card_info[]`, line and ADSL status, polling state machine, command buffers, command URBs, and firmware-loaded hardware state. Sysfs writes can change modem card-data configuration and start/stop state in hardware, but the driver does not persist those settings to disk.

## Dependencies And Integration Points
The driver depends on USB core, firmware loader, sysfs attribute groups, `usbatm`, Linux ATM, and firmware files. It integrates with `usbatm` through `bind`, `heavy_init`, `unbind`, `atm_start`, endpoint definitions, and RX/TX padding values.

## Risks And Edge Cases
Command transfers require serialized send/receive URBs and timeouts; failures disable polling until userspace restarts it. The firmware path contains multiple device-memory writes with limited recovery if firmware partially starts. Sysfs `adsl_config` accepts index/value pairs and requires `CAP_NET_ADMIN`, but malformed input returns early. Poll cancellation depends on `CXPOLL_SHUTDOWN` and delayed work ordering. Historical devices vary between interrupt and bulk command endpoints.

## Test Signals
Test both already-firmware-loaded and cold firmware paths. Verify firmware request names, MAC retrieval, `/sys/bus/usb/.../cxacru` attributes, `adsl_state` start/stop/restart/poll writes, and ATM carrier transitions. Exercise command timeout paths by unplugging during polling. Confirm RX/TX padding interworks with `usbatm` cell traffic.
