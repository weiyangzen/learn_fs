# sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos.h

## Purpose
`dsp_spos.h` is the low-level constants and inline-helper header for the CS46xx new DSP SPOS path. It is compiled only under `CONFIG_SND_CS46XX_NEW_DSP` and supplies DSP memory sizes, memory offsets, relocation opcode identifiers, fixed sample-buffer/task/SCB addresses, SCB field offsets, stream configuration bit masks, SP-only register addresses, channel-status bit wrapping, and direct SCB patch helpers.

## Important APIs and constants
The header defines DSP memory areas (`DSP_CODE_BYTE_SIZE`, `DSP_PARAMETER_BYTE_SIZE`, `DSP_SAMPLE_BYTE_SIZE` and offsets), relocation masks/opcodes (`WIDE_INSTR_MASK`, `WIDE_LADD_INSTR_MASK`, `enum wide_opcode`), sample buffer addresses (`PCM_READER_BUF1`, `MIX_SAMPLE_BUF*`, SPDIF buffers, snoop buffers), SCB/task addresses (`SPOSCB_ADDR`, `TIMINGMASTER_SCB_ADDR`, `MASTERMIX_SCB_ADDR`, `HFG_TREE_SCB`, etc.), field offsets (`SCBsubListPtr`, `SCBfuncEntryPtr`, `SCBVolumeCtrl`), stream config flags (`RSCONFIG_*`), and SP register addresses (`SP_SPDOUT_CONTROL`, `SP_SPDIN_CONTROL`, `SP_SPDOUT_CSUV`, and related FIFO/status registers).

## Control flow and helpers
`_wrap_all_bits()` reverses bit order in a byte for IEC958 channel-status representation. `cs46xx_dsp_spos_update_scb()` patches an existing SCB's `sub_list_ptr` and `next_scb` dword in DSP memory and marks the descriptor updated for resume replay. `cs46xx_dsp_scb_set_volume()` writes inverted left/right target/current volume values to the two volume-control dwords and caches the requested values in the descriptor.

## State and persistence behavior
The header itself stores no state, but its helpers mutate both DSP memory and `dsp_scb_descriptor` flags (`updated`, `volume_set`, `volume[]`). Those flags are consumed by `cs46xx_dsp_resume()` to restore runtime changes after BA1 memory is cleared and rewritten.

## Dependencies and integration points
The helpers require `struct snd_cs46xx`, `struct dsp_scb_descriptor`, and `snd_cs46xx_poke()` from the broader driver. The constants are used by `dsp_spos.c`, `dsp_spos_scb_lib.c`, and `cs46xx_lib.c` for SCB construction, PCM pointer reads, period programming, SPDIF controls, and proc dumps.

## Risks
Address and offset constants are hardware/firmware ABI. A wrong constant can redirect DSP task links, corrupt sample buffers, or poke an SP register through the wrong route. Volume writes invert ALSA-style values with `0xffff - value`, so callers must pass the expected range. `cs46xx_dsp_spos_update_scb()` assumes both link pointers are non-null and valid descriptor addresses.

## Test signals
Useful signals include correct PCM pointer progression from SCB address reads, working runtime SCB link/unlink operations, volume changes surviving resume, IEC958 channel-status bytes matching ALSA controls after bit wrapping, SPDIF input/output control register effects, and no DSP graph corruption in procfs SCB dumps.
