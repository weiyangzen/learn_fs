# sources/distributed-fs/ceph-client/sound/pci/lola/lola_proc.c

## Purpose
This debug-only file creates ALSA proc entries for inspecting Lola codec widgets, issuing direct codec read/write commands, and dumping BAR/DSD registers.

## Important APIs, Types, and Functions
`lola_proc_debug_new()` creates `codec`, `codec_rw`, and `regs` proc entries when `CONFIG_SND_DEBUG` links this file. `lola_proc_codec_read()` prints vendor/function/specific caps and walks the same NID order as probe: capture audio widgets, playback audio widgets, input pins, output pins, optional clock, optional mixer. `lola_proc_codec_rw_write/read()` provides direct four-integer codec command access and returns the last response. `lola_proc_regs_read()` dumps BAR0/BAR1 ranges and DSD status/LPIB/control/BDL registers.

## Control Flow
Probe calls `lola_proc_debug_new()` after PCM and mixer creation. Read callbacks query live codec/register state on demand. The read/write proc path parses user input lines as `id verb data extdata`, calls `lola_codec_read()`, and stores results in `chip->debug_res` and `chip->debug_res_ex`.

## State and Persistence
The file adds only transient debug response fields in `struct lola`; it does not persist data. Proc reads may have hardware side effects if the underlying codec verbs do.

## Dependencies and Integration Points
It depends on ALSA proc helpers, codec verb helpers, widget constants from `lola.h`, and `CONFIG_SND_DEBUG` build gating in the Makefile/header. It is explicitly not present in normal builds.

## Risks
`codec_rw` is powerful direct hardware access and can change or query arbitrary codec verbs, so keeping it debug-only matters. Dump callbacks issue live codec reads without extensive error handling. Register dumps assume fixed DSD count of 32, matching BAR1 layout constants.

## Test Signals
With `CONFIG_SND_DEBUG`, proc entries should appear under the card and show coherent widget caps matching probe. `codec_rw` should return expected response pairs for benign read verbs. `regs` should show changing DSD LPIB/STS during active PCM streams. Non-debug builds should compile without this object and use the no-op `lola_proc_debug_new` macro.
