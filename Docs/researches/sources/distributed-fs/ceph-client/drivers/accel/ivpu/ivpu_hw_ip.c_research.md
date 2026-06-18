## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_ip.c

### Purpose
`ivpu_hw_ip.c` implements IP-side register programming for host subsystem configuration, idle generation, power islands, clocks/resets, NoC handshakes, snoop/TBU setup, firmware CPU boot, watchdog disable, IRQ enable/clear/dispatch/diagnostics, IPC FIFO access, doorbells, and 50xx fabric/power-delay controls.

### Important APIs, Types, And Functions
Public APIs include `ivpu_hw_ip_host_ss_configure()`, idle-gen enable/disable, `ivpu_hw_ip_pwr_domain_enable()`, `ivpu_hw_ip_host_ss_axi_enable()`, `ivpu_hw_ip_top_noc_enable()`, perf timer read, snoop disable, TBU MMU enable, SOC CPU boot, watchdog disable, diagnostics, IPC RX count/address and TX write, IRQ enable/disable/clear/handlers, and doorbell set. Internal helpers are split into 37xx and 40xx/50xx/60xx variants.

### Control Flow
Host SS configuration checks BAR readiness on 37xx, clears resets, and verifies NoC handshake lines are idle. Power-domain enable programs 50xx delay registers when needed, enables trickle/main power island bits, waits status, enables host clocks, disables isolation, asserts resets, and marks 37xx DPU active. AXI and top NoC enable set QREQN bits and verify QACCEPTN/QDENY. Firmware boot disables snoop, enables TBU SSID valid bits, drives SOC CPU/sets entry point by generation, and logs warm/cold mode. IRQ handlers clear status, dispatch MMU event/global errors, IPC FIFO handling, watchdog recovery, and NOC firewall accounting.

### State, Persistence, And Dependencies
State persists in BAR0 RegV registers: clocks, resets, power islands, NoC handshakes, snoop/TBU overrides, CPU entry point, watchdog, IPC FIFO, doorbells, and IRQ masks/status. Dependencies include 37xx/40xx register maps, reg I/O helpers, firmware entry points, MMU IRQ handlers, IPC IRQ handler, PM recovery, and hardware generation helpers.

### Integration Points
`ivpu_hw.c` calls this during power-up and firmware boot. `ivpu_ipc.c` uses the IPC FIFO wrappers. Job/cmdq code uses doorbells through `ivpu_hw_db_set()`. MMU and PM recovery receive IRQ callbacks from this layer.

### Risks
Generation-specific helpers are easy to mix because 37xx and 40xx offsets often share names but not semantics. The `pwr_island_drive_37xx()`/`pwr_island_drive_40xx()` bodies reference opposite register-prefix names, which should be verified against shared offsets or corrected if unintended. Handshake polling returns `-EIO` on unexpected bits but does not retry except through higher-level sequencing. IRQ FIFO draining must purge all messages or future IPC interrupts may stop.

### Test Signals
Test host SS configuration, power island enable, NoC handshakes, firmware boot entry programming for cold/warm and 37xx/40xx/60xx, snoop override with and without forced snoop, TBU valid bits, watchdog recovery IRQs, MMU/IPC IRQ dispatch, NOC firewall counter, IPC FIFO drain, and doorbell stride/index writes.
