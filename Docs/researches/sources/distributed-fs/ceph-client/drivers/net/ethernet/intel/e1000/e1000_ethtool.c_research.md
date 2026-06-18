# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_ethtool.c

Purpose: ethtool support and offline diagnostics for the legacy Intel PRO/1000 `e1000` driver. It translates kernel ethtool requests into driver/hardware state changes for link settings, flow control, register and EEPROM access, ring sizing, self-tests, Wake-on-LAN, LED identification, interrupt coalescing, and statistics.

Important APIs, types, and functions:

- Stats metadata: `struct e1000_stats`, `E1000_STAT()`, `E1000_NETDEV_STAT()`, and `e1000_gstrings_stats[]` map ethtool statistic names to offsets in either `struct e1000_adapter` or `struct net_device`. `e1000_get_ethtool_stats()` uses the metadata to copy 32-bit or 64-bit values into the ethtool buffer after `e1000_update_stats()`.
- Link settings: `e1000_get_link_ksettings()` reports supported/advertised modes, copper/fiber port type, current speed/duplex, autoneg, and MDI/MDI-X state. `e1000_set_link_ksettings()` validates MDI-X rules, serializes through `__E1000_RESETTING`, updates autoneg advertisement or forced speed/duplex through `e1000_set_spd_dplx()`, updates `hw->mdix`, and resets or restarts the device.
- Link and pause: `e1000_get_link()` forces a fresh hardware link check when carrier is down. `e1000_get_pauseparam()` and `e1000_set_pauseparam()` expose and update RX/TX pause and flow-control autoneg, then either restart the adapter or call `e1000_setup_link()`/`e1000_force_mac_fc()`.
- Register dump: `e1000_get_regs_len()` returns 32 registers. `e1000_get_regs()` fills MAC registers, descriptor pointers, interrupt timers, PHY type and PHY-specific diagnostic registers for IGP or M88 PHYs, idle/receive errors, 1000T status, and management control on newer copper MACs.
- EEPROM access: `e1000_get_eeprom_len()`, `e1000_get_eeprom()`, and `e1000_set_eeprom()` expose hardware EEPROM with vendor/device magic validation, odd-byte read-modify-write preservation, endianness conversion, SPI multiword reads where supported, and checksum update when the modified range includes the checksum region.
- Ring parameters: `e1000_get_ringparam()` reports per-MAC descriptor limits and active ring counts. `e1000_set_ringparam()` clamps and aligns requested counts, serializes through `__E1000_RESETTING`, optionally takes the device down, allocates replacement ring structs, sets up new resources before freeing old ones, then restarts the adapter or restores old rings on failure.
- Offline tests: `e1000_reg_test()`, `e1000_eeprom_test()`, `e1000_intr_test()`, `e1000_loopback_test()`, and `e1000_link_test()` provide ethtool self-test data. Helpers allocate temporary descriptor rings, build/check loopback frames, configure PHY/MAC loopback for different MAC/PHY generations, and clean up afterward.
- WoL/LED/coalesce: `e1000_wol_exclusion()`, `e1000_get_wol()`, and `e1000_set_wol()` enforce device/port-specific wake capabilities. `e1000_set_phys_id()` drives hardware LEDs for ethtool identify. `e1000_get_coalesce()` and `e1000_set_coalesce()` expose RX interrupt throttle on 82545+ hardware.
- Registration: `e1000_ethtool_ops` holds all implemented operations, and `e1000_set_ethtool_ops()` installs it on the netdev.

Control flow:

- Ettool operations generally begin by obtaining `struct e1000_adapter *adapter = netdev_priv(netdev)` and then operate on `adapter->hw`, `adapter->tx_ring`, `adapter->rx_ring`, and adapter flags.
- Link-setting changes serialize against resets by spinning on `test_and_set_bit(__E1000_RESETTING, &adapter->flags)`. If the netdev is running, they call `e1000_down()` and `e1000_up()` to apply changes; otherwise they call `e1000_reset()`. The reset bit is cleared on all normal error paths.
- Ring resizing takes the same reset bit, optionally downs the running adapter, allocates new TX/RX ring arrays, swaps them into the adapter, sets counts for all queues, pre-allocates resources if running, swaps back to free old resources, restores the new rings, and calls `e1000_up()`. Allocation/setup failures restore old ring pointers, free partial allocations, restart the old adapter if needed, and clear the reset bit.
- Offline diagnostics set `__E1000_TESTING`. Offline mode saves autoneg/speed/duplex state, performs link test before reset, closes a running interface or resets a stopped one, runs register/EEPROM/interrupt/loopback tests with resets between them, restores link configuration, resets, clears testing, and reopens if it was originally running. Online mode only runs link test and marks other tests passed by default.
- Interrupt test temporarily requests the device IRQ with a test handler, masks all interrupts, forces individual cause bits through `ICS`, observes `adapter->test_icr`, distinguishes shared versus unshared IRQ behavior, disables interrupts, and frees the IRQ.
- Loopback test builds temporary TX/RX rings directly in hardware registers, configures PHY or transceiver loopback based on media/MAC generation, sends 64 frames per loop iteration by moving TDT, polls RX buffers for signature bytes, then clears loopback and frees all temporary DMA mappings.
- EEPROM get/set compute first and last EEPROM word from byte offset/length. Reads allocate just the requested word span; writes allocate a full EEPROM-sized buffer, preserve partial edge words when offsets are odd, convert endianness before and after byte copy, write the word span, and update the EEPROM checksum when needed.

State and persistence behavior:

- Link, pause, MDI-X, interrupt throttle, ring counts, WoL, and autoneg settings are runtime adapter/hardware state. Some of these mirror persistent defaults from EEPROM but this file usually does not persist them unless the explicit EEPROM write operation is used.
- EEPROM writes are persistent hardware modifications and are guarded by an ethtool magic value `vendor_id | device_id << 16`. Checksum is updated for changes affecting the checksum-covered range.
- Offline testing temporarily mutates hardware registers, descriptor registers, PHY loopback bits, IRQ handlers, and adapter state bits. It saves and restores autoneg advertisement, forced speed/duplex, and autoneg boolean around the destructive portion.
- Statistics are read from live adapter/netdev memory through offset metadata. This couples ethtool stat layout tightly to `struct e1000_adapter` and `struct net_device` field sizes.
- WoL settings update `adapter->wol` and device wakeup enablement. Port and device exclusions prevent advertising unsupported wake modes.

Dependencies and integration points:

- Depends on `e1000.h` for adapter/ring definitions, state bits, register macros (`er32`, `ew32`, `E1000_WRITE_FLUSH()`), constants, logging, and core function prototypes.
- Depends on low-level hardware helpers from `e1000_hw.c`/`e1000_hw.h`, including EEPROM read/write/checksum, PHY register access, PHY reset, link setup, flow-control forcing, LED control, speed/duplex discovery, and link checking.
- Integrates with the kernel ethtool API through `struct ethtool_ops`, `ethtool_link_ksettings`, `ethtool_eeprom`, `ethtool_ringparam`, `ethtool_test`, `ethtool_wolinfo`, `ethtool_pauseparam`, and coalesce structures.
- Uses PCI/DMA APIs for offline descriptor rings and IRQ APIs for interrupt testing. Uses SKB allocation for loopback frames and raw allocated RX buffers for test receives.

Risks and maintenance concerns:

- Offline tests are intentionally invasive: register tests write many MAC registers, interrupt tests replace the IRQ handler, and loopback tests reprogram descriptor registers. They must only run while the adapter is isolated by `__E1000_TESTING` and, for offline mode, after closing or resetting the normal datapath.
- `e1000_set_link_ksettings()` and `e1000_set_pauseparam()` spin-sleep on `__E1000_RESETTING`. Any new caller that holds locks needed by reset/down/up could deadlock.
- Ring resize swaps adapter ring pointers several times to free old resources after new resources are created. Error paths must preserve pointer ownership exactly or risk leaking DMA memory or freeing active rings.
- Stats extraction uses raw offsets and assumes field sizes are either `u32` or `u64`. Any structure field type change in `e1000_adapter` can silently break ethtool stats unless `e1000_gstrings_stats[]` is updated.
- EEPROM writes allocate `max_len` bytes but only initialize edge words and copied bytes before writing the requested word span; the targeted span is covered, but changes to this logic must preserve odd offset behavior and checksum handling.
- The loopback receive wait condition is timing-sensitive and uses DMA syncs plus signature-byte checks. Slow hardware, virtualization, or unusual descriptor counts can expose timeout or false-failure behavior.
- WoL support has several device/port exclusions, including quad/dual-port function restrictions. Adding device IDs requires validating wake capabilities per port, not just per MAC family.
- Coalesce conversion treats values `0..4` specially and rejects `2`; callers and documentation must match this legacy ITR encoding.

Test signals:

- Build and link as part of `e1000.o` with `CONFIG_E1000=m/y`.
- Ettool coverage: `ethtool -i`, `-k`, `-S`, `-d`, `-e`, EEPROM write with valid/invalid magic, `-g/-G`, `-a/-A`, `-c/-C`, `-p`, `-s`, `--show-eee` absence expectations, `--test online`, and `--test offline`.
- Link setting matrix: copper versus fiber, autoneg on/off, forced 10/100/1000 where supported, MDI/MDI-X auto/manual validation, and carrier-down fresh link checks.
- Ring resize under traffic and while stopped, including allocation-failure injection and descriptor count alignment on pre-82544 versus newer MACs.
- Offline diagnostics on representative 82542/82543/82544/82545/82546/82540/82541/82547 devices or emulations where available, with attention to PHY loopback variants and shared IRQ behavior.
- WoL get/set on unsupported devices, dual/quad-port function B exclusions, KSP3 unicast exclusion, and `device_can_wakeup()` false cases.
- Interrupt throttle programming on 82545+ and rejection on older MACs or invalid usec values.
