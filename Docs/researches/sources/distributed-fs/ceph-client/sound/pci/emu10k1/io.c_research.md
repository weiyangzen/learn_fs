# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/io.c

## Purpose
`io.c` centralizes low-level EMU10K1 register access and hardware-control primitives. It provides serialized PTR/DATA and PTR2/DATA2 access, SPI/I2C codec transactions, E-MU 1010 FPGA register and route access, firmware bitstream upload, interrupt-mask manipulation, voice loop/interrupt control, wait timing, and AC97 read/write callbacks.

## Important APIs, Types, and Functions
Exported/common APIs include `snd_emu10k1_ptr_read()`, `snd_emu10k1_ptr_write()`, `snd_emu10k1_ptr_write_multiple()`, `snd_emu10k1_ptr20_read()`, `snd_emu10k1_ptr20_write()`, `snd_emu10k1_spi_write()`, `snd_emu10k1_i2c_write()`, FPGA helpers such as `snd_emu1010_fpga_write()`, `snd_emu1010_fpga_read()`, link helpers, `snd_emu1010_update_clock()`, `snd_emu1010_load_firmware_entry()`, interrupt enable/disable helpers, loop-stop helpers, `snd_emu10k1_wait()`, and AC97 callbacks. `check_ptr_reg()` validates encoded register/channel fields for primary pointer access.

## Control Flow
Pointer reads and writes compose `(reg << 16) | channel`, lock `emu->emu_lock`, write the pointer port, and read/write data. Bitfield-encoded registers perform read-modify-write masks. SPI and I2C functions serialize with dedicated spinlocks and poll status bits with timeouts. FPGA writes require the E-MU 1010 mutex or acquire it through a guard helper, strobing GPIO bits to latch register/value pairs. Interrupt helpers modify INTE, voice interrupt masks, half-loop masks, and loop-stop registers. `snd_emu10k1_voice_clear_loop_stop_multiple_atomic()` carefully times low/high voice release against the hardware sample cycle.

## State and Persistence
Hardware registers are the primary state. Software state includes locks, `emu->emu1010.word_clock`, card capability flags, and firmware blob content passed to FPGA upload. Register writes persist until device reset, suspend/resume restore, or another module changes them; nothing is stored on disk.

## Dependencies and Integration Points
All higher-level EMU10K1 modules depend on this file for register access. `emupcm.c` uses pointer writes, loop-stop, and interrupt helpers; `irq.c` uses interrupt-disable and voice ack helpers; `timer.c` uses `snd_emu10k1_intr_enable/disable`; `emuproc.c` uses pointer and FPGA reads; main initialization uses FPGA firmware upload and clock update. AC97 integration is via `struct snd_ac97` bus callbacks.

## Risks
The file touches device registers directly and is highly concurrency-sensitive. Incorrect locking can corrupt the shared PTR/DATA address latch. SPI/I2C polling paths can fail or stall hardware; `snd_emu10k1_i2c_write()` has a timeout counter that is not reset per retry, so timeout behavior must be read carefully before modification. FPGA reads can trigger GPIO IRQs as a side effect. Atomic loop-stop clearing disables interrupts for short but deliberate windows and can return `-EAGAIN` when timing is disturbed. Firmware upload bit-bangs GPIO and depends on hardware wiring assumptions.

## Test Signals
Regression tests need hardware or emulation. Signals include stable AC97 codec reads/writes, no pointer-register races under concurrent PCM/MIDI/proc access, I2C/SPI timeout logging only on real failures, E-MU 1010 clock LEDs/rate selection matching input clock, and successful synchronized EFX playback starts. Lockdep and IRQ latency tracing are useful around loop-stop atomic release and FPGA access.
