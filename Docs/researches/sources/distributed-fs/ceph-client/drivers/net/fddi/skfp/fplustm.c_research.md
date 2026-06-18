# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/fplustm.c

## Purpose
`fplustm.c` is the FORMAC+ tag-mode hardware driver. It initializes FORMAC/RBC memory and BMU queues, builds claim/beacon frames in adapter memory, manages ring-up/down and MAC interrupts, maintains MAC counters and multicast CAM state, controls receive modes, handles restricted-token monitoring, and supports ESS FIFO/TSYNC changes.

## Important APIs, Types, And Functions
Major entry points include `init_fplus()`, `mac_update_counter()`, `set_formac_tsync()`, `formac_tx_restart()`, `mac2_irq()`, `mac3_irq()`, `config_mux()`, `sm_mac_check_beacon_claim()`, `sm_ma_control()`, `sm_mac_get_tx_state()`, multicast functions, `mac_set_rx_mode()`, `rtm_irq()`, `rtm_set_timer()`, and `formac_reinit_tx()`. Internal setup helpers include `init_mac()`, `init_ram()`, `smt_split_up_fifo()`, `init_tx()`, `init_rx()`, `init_rbc()`, `build_claim_beacon()`, and `set_formac_addr()`.

## Control Flow
`init_fplus()` seeds default receive mode, group address, register pointers, counters, PCI fixups, then calls `init_mac(all=1)`. `init_mac()` places FORMAC in init/memory mode, optionally clears RBC RAM, splits FIFO space, initializes TX/RX queues and RBC pointers, builds claim/beacon/directed-beacon frames, programs thresholds, mode registers, timers, RTM, and BMU reset/repair for partial resets. Ring events in `mac2_irq()` update cached status, toggle receive/transmit through `mac_ring_up()`, and queue RMT events for ring op/non-op, beacons, claims, TRT expiry, duplicate address, and TX state changes. `sm_ma_control()` is the RMT-facing MAC command interface.

## State And Persistence
State is in `smc->hw.fp` (FIFO layout, receive mode, error stats, multicast table, FORMAC status shadows, queue pointers), `smc->hw.mac_ring_is_up`, MAC counters in `smc->mib.m[MAC0]`, and ESS TSYNC/FIFO flags. Hardware state persists only while the adapter is running: FORMAC registers, adapter buffer memory, CAM entries, BMU queues, and RTM timer.

## Dependencies And Integration Points
It depends on `supern_2.h` FORMAC bits, `skfbi.h` register access macros, Linux bit reversal and Ethernet address helpers, descriptor/queue types from `fplustm.h`, OS-specific descriptor repair/fill callbacks, LLC TX restart, SMT/RMT/CFM/ESS events, and hardware timer helpers.

## Risks And Edge Cases
Register sequencing and busy waits (`CHECK_NPP`, `CHECK_CAM`) are timing-sensitive. FIFO splitting assumes valid descriptor counts and exact 32 KB/64 KB FORMAC memory layout. Multicast accounting separates permanent SMT slots from OS slots and can leak counts if deletion support is added incorrectly. Receive mode changes rewrite hardware address filters immediately. Counter high-word handling depends on interrupts catching 16-bit hardware counter wrap.

## Test Signals
Validate full and partial MAC initialization, adapter RAM clearing, claim/beacon frame content, ring-up/down RMT events, duplicate-address handling, receive overflow counters, parity/error panic paths, TX restart after abort/lock, multicast add/clear/update including canonical conversion, promisc/allmulti/NSA modes, restricted token timer interrupt, ESS TSYNC/FIFO reinit, and descriptor repair after partial reset.
