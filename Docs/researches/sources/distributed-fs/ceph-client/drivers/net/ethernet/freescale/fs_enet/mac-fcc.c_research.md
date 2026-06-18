# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fs_enet/mac-fcc.c

## Purpose
Implements the FCC backend for `fs_enet` on CPM2/PQ2 systems. It maps FCC registers/parameter RAM, programs FCC Ethernet operation on link-up, handles multicast filtering, interrupts, register dumps, and Tx restart errata recovery through `fs_fcc_ops`.

## Important APIs, Types, and Functions
The exported object is `const struct fs_ops fs_fcc_ops`. Important functions include `do_pd_setup`, `setup_data`, `allocate_bd`, `restart`, `stop`, `set_multicast_list`, NAPI event helpers, `get_int_events`, `clear_int_events`, `get_regs`, and `tx_restart`. Hardware access is through FCC register macros and CPM commands via `fcc_cr_cmd`.

## Control Flow and State
Setup maps three DT resources (FCC core, Ethernet parameter RAM, FCC continuation registers), stores CPM immediate memory, and allocates DPRAM for internal buffers. Restart disables RX/TX, clears parameter RAM, writes Rx/Tx BD base physical addresses, MRBLR, function codes, internal buffer pointers, CRC presets, counters, station/group addresses, frame size limits, RMII/speed/duplex mode, initializes BDs, issues `CPM_CR_INIT_TRX`, clears/enables events, and enables FCC Ethernet. `tx_restart` scans backward from hardware TBPTR to adjust retransmission state, toggles transmitter enable, and issues `CPM_CR_RESTART_TX`.

## Dependencies and Integration Points
Depends on CPM2 headers, `cpm_command`, `cpm_muram_alloc`, OF mapping/IRQ APIs, common descriptor helpers from `fs_enet.h`, and phylink-provided speed/duplex/interface from `fs_enet-main.c`.

## Risks and Test Signals
Risks include DPRAM leaks, resource unmap omissions, group-address low/high typo or stale cached multicast state, TBPTR recovery off-by-one errors, RMII speed bit inversion, and unmasked event reads causing interrupt loops. Test signals include FCC probe/link-up, multicast/promiscuous updates, TX underrun/late-collision recovery, ethtool register dumps, NAPI event masking, and CPM command failure instrumentation.
