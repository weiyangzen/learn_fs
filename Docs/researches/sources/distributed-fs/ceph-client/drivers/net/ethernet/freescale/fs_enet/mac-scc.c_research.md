# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mac-scc.c

## Purpose
Implements the SCC Ethernet backend for `fs_enet` on CPM1/CPM2 Serial Communications Controllers. It programs SCC registers and parameter RAM, allocates BD rings from CPM multi-user RAM, handles multicast mode, events, and Tx restart through `fs_scc_ops`.

## Important APIs, Types, and Functions
The exported object is `const struct fs_ops fs_scc_ops`. Important functions are `scc_cr_cmd`, `do_pd_setup`, `setup_data`, `allocate_bd`, `restart`, `stop`, `set_multicast_list`, NAPI event helpers, `get_int_events`, `clear_int_events`, `get_regs`, and `tx_restart`.

## Control Flow and State
Setup maps SCC and SCC Ethernet parameter resources and initializes event masks/hash caches. BD allocation reserves CPM MURAM and stores the virtual ring base. Restart disables SCC RX/TX, clears parameter RAM byte-by-byte, writes Rx/Tx BD offsets, function codes, MRBLR, CRC presets, counters, pad/retry/frame-size values, station address, initializes BDs, issues `CPM_CR_INIT_TRX`, clears/enables events, programs GSMR/DSR/PSMR Ethernet mode, applies duplex and multicast/promiscuous settings, and enables Rx/Tx. Stop masks events, clears enable bits, and cleans BDs.

## Dependencies and Integration Points
Depends on CPM command/MURAM APIs, SCC register definitions from architecture headers, OF IRQ/mapping, and common `fs_enet` descriptor/NAPI logic. `fs_enet-main.c` selects it for CPM SCC compatible strings when enabled.

## Risks and Test Signals
Risks include ignored `do_pd_setup` failures in `setup_data`, MURAM allocation/free mismatches, register dump size using pointer-size instead of parameter RAM structure size, SCC stop timeout logic, and multicast group programming correctness. Test signals include SCC probe on CPM1/CPM2, link-up/down, full-duplex mode, multicast/allmulti/promisc changes, Tx restart via CPM command, register dumps, and NAPI interrupt masking.
