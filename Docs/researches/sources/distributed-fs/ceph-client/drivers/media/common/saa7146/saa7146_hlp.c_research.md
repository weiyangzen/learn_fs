# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_hlp.c

Purpose: low-level SAA7146 video helper routines for HPS scaling, output format programming, DMA register programming, capture engine RPS programs, clipping disable, and source/sync selection.

Important APIs/functions: exported `saa7146_set_hps_source_and_sync()` and `saa7146_write_out_dma()`. `saa7146_set_capture()` is the main capture-programming entry used by video buffer activation. Internal scaling helpers calculate horizontal/vertical scaler registers from input/output dimensions, field mode, and flips; DMA helpers program packed and planar formats.

Control flow: capture activation recalculates HPS window and output format, disables clipping, toggles alternate field state, writes DMA descriptors for packed or planar formats, builds an RPS0 program that waits for field boundaries, enables DMAs, stops them, interrupts, then starts RPS0.

State/persistence: hardware register state is updated on each capture. `vv->last_field`, `current_hps_source`, `current_hps_sync`, `hflip`, and `vflip` influence programming. No durable persistence.

Dependencies/integration: used by `saa7146_video.c` buffer activation. Depends on SAA7146 register constants, RPS macros, format metadata, VB2-built page tables, and extension-selected TV standard geometry.

Risks/test signals: scaling math rejects vertical zoom but mostly ignores return values; DMA offsets for planar/user buffers have FIXME notes; flips and alternate fields are fragile. Test signals include format/field matrix captures, planar 4:2:0/4:2:2 offsets, hflip/vflip boundaries, NTSC/PAL standard sizes, and RPS interrupt completion.
