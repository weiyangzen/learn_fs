# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctdaio.c

Purpose: Digital Audio I/O resource manager for ctxfi, handling DAO outputs, DAI inputs, device index translation, DAIO enable/disable, and audio input mapper programming.

Important APIs and types: `daio_mgr_create/destroy`, `get_daio_rsc`, `put_daio_rsc`, `dao_rsc_init/uninit/reinit`, `dai_rsc_init/uninit`, DAO ops (`set_spos`, `commit_write`, `set_left_input`, `set_right_input`, clear inputs), and DAI ops (`set_srt_srcl/srcr`, `set_srt_msr`, enable SRC/SRT, commit). Static maps `idx_20k1` and `idx_20k2` provide left/right resource indexes per `DAIOTYP`.

Control flow: a DAIO allocation first reserves the unique type bit, then allocates either `struct dao` for outputs or `struct dai` for inputs. DAO init disables the target output, initializes DAO config including passthrough/MSR, re-enables it, and allocates mapper pointer slots. DAI init configures sample-rate tracker control. DAO input setters allocate imapper entries for each conjugate, clear prior mappings, map input output slots to DAO left/right users, and add entries to the manager list.

State and persistence: `struct daio_mgr` stores a bitset resource allocator, locks, imapper list, and default init imap entry. DAO objects own imapper arrays and control blocks. Hardware mapping state is committed through `hw->daio_mgr_*` callbacks.

Dependencies and integration: depends on `ctresource`, `ctimap`, and `cthardware`; `ctatc.c` uses it to allocate all physical line, S/PDIF, mic, and RCA endpoints and to connect mixer output ports.

Risks and test signals: each DAIO type is single-tenant; requesting an already-used type returns `-ENOENT`. Mapper deletion restores an initial zero mapping when list becomes empty. Tests: allocate/free every supported type on 20K1 and 20K2, invalid type rejection, DAO left/right remap replacement, S/PDIF passthrough reinit, and imapper list empty restoration.
