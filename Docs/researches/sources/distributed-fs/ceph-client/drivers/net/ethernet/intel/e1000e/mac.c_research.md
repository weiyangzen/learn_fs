# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/mac.c

## Purpose

`mac.c` provides generic MAC-level services shared by e1000e hardware families. It handles PCIe bus metadata, receive address and multicast/VLAN filter programming, base counter clearing, copper/fiber/serdes link checks, flow-control setup and negotiation, hardware/NVM semaphore acquisition, LED control, PCIe master disable, and adaptive interframe spacing. Family files such as `ich8lan.c` install these helpers into their operation tables unless silicon-specific behavior is required.

## Important APIs, Types, And Functions

Bus helpers are `e1000e_get_bus_info_pcie`, `e1000_set_lan_id_multi_port_pcie`, and `e1000_set_lan_id_single_port`. Address/filter APIs include `e1000_clear_vfta_generic`, `e1000_write_vfta_generic`, `e1000e_init_rx_addrs`, `e1000_check_alt_mac_addr_generic`, `e1000e_rar_get_count_generic`, `e1000e_rar_set_generic`, and `e1000e_update_mc_addr_list_generic`.

Link APIs include `e1000e_check_for_copper_link`, `e1000e_check_for_fiber_link`, `e1000e_check_for_serdes_link`, `e1000e_setup_link_generic`, `e1000e_setup_fiber_serdes_link`, `e1000e_config_collision_dist_generic`, `e1000e_config_fc_after_link_up`, `e1000e_force_mac_fc`, `e1000e_set_fc_watermarks`, `e1000e_get_speed_and_duplex_copper`, and `e1000e_get_speed_and_duplex_fiber_serdes`. LED APIs include default validation, ID initialization, setup, cleanup, blink, on, and off helpers. Synchronization and bus control APIs include `e1000e_get_hw_semaphore`, `e1000e_put_hw_semaphore`, `e1000e_get_auto_rd_done`, `e1000e_set_pcie_no_snoop`, and `e1000e_disable_pcie_master`.

## Control Flow

Receive initialization writes RAR0 with `hw->mac.addr`, clears remaining RAR entries, and then multicast updates rebuild `hw->mac.mta_shadow` from a packed multicast address list before programming the whole MTA array. Alternate MAC detection reads NVM pointer words, rejects invalid or multicast alternate addresses, and writes a valid alternate address into RAR0.

Generic copper link check only runs when `mac->get_link_status` is set. It probes PHY link, checks downshift, returns configuration errors for forced speed/duplex, configures collision distance, and resolves flow control after link-up. Fiber/serdes checks watch RXCW/TXCW/STATUS and force link when auto-negotiation fails with signal or idle reception, then restore autoneg when ordered sets return.

Flow-control setup starts by resolving default NVM policy, copies requested mode to current mode, delegates physical-interface setup, initializes pause MAC address/type/timer registers, and writes watermarks. After link-up, copper and serdes code read local and partner pause advertisements, apply IEEE pause resolution including asymmetric cases and half-duplex disabling, then force CTRL/PCS flow-control bits.

## State And Persistence Behavior

The file primarily mutates volatile hardware state: RAR/RAH/RAL, VFTA, MTA, CTRL, TXCW, PCS, FCRTL/FCRTH, LEDCTL, GCR, AIT, SWSM, and status/control registers. Persistent reads occur through NVM for default flow control, alternate MAC address, and LED defaults, but this file does not commit NVM writes. Software state updated includes `hw->bus.func`, `hw->bus.width`, `hw->mac.txcw`, LED cached modes, `mac->mta_shadow`, `mac->serdes_has_link`, `mac->autoneg_failed`, `hw->fc.current_mode`, and adaptive IFS counters.

## Dependencies And Integration Points

`mac.c` depends on Linux PCI helpers, `linux/bitfield.h`, e1000e register access macros, PHY read/write helpers, NVM read helpers, Ethernet address helpers, and generic constants from the driver headers. It is integrated through `struct e1000_mac_operations`: family modules selectively use generic implementations for address filters, link, flow control, LEDs, counters, bus info, and PCIe shutdown.

## Risks

Flow-control negotiation is subtle because requested, advertised, partner, media, autoneg-failed, and duplex states interact. Incorrect resolution can cause pause-frame loss, stalls, or asymmetric throughput problems. RAR writes require little-endian packing and posted-write flushes; missing flushes can affect bridges that merge writes. Semaphore loops can timeout if firmware owns SWSM bits. Serdes forced-link recovery depends on sticky RXCW bits and can oscillate if state flags are mishandled. Multicast table programming can add latency on RT kernels, which is why the code conditionally flushes during large posted-write sequences.

## Test Signals

Signals include correct permanent and alternate MAC address programming, VLAN and multicast filtering behavior, no link regressions across copper/fiber/serdes adapters, correct pause-frame negotiation for full/tx/rx/none modes, successful forced-link fallback with non-autoneg partners, clean PCIe master disable during reset, stable LED identify operations, and adaptive IFS register changes only when collision/tx deltas justify them.
