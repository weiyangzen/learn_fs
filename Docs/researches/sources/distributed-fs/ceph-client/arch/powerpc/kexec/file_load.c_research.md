# sources/distributed-fs/ceph-client/arch/powerpc/kexec/file_load.c

## Purpose
Provides common PowerPC helpers for `kexec_file_load`, covering kdump command-line construction and purgatory symbol initialization.

## Important APIs, Types, And Functions
Defines `setup_kdump_cmdline` and `setup_purgatory`. Uses `SLAVE_CODE_SIZE` for the first 0x100 bytes copied into purgatory and generic `kexec_purgatory_get_set_symbol`.

## Control Flow
`setup_kdump_cmdline` allocates a command-line buffer, prepends `elfcorehdr=0x<addr> `, validates the combined length against `COMMAND_LINE_SIZE`, copies the existing command line, and NUL terminates. `setup_purgatory` reads the current purgatory start buffer to preserve the master entry word, copies slave code from the new kernel into purgatory, restores the master entry, writes the buffer back, and sets `kernel` and `dt_offset` purgatory symbols.

## State And Persistence
Mutates allocated command-line memory and purgatory symbol storage embedded in the kexec image. No durable storage is used.

## Dependencies And Integration Points
Used by `elf_64.c` and `file_load_64.c`. Depends on generic kexec purgatory APIs, PowerPC boot convention for slave code, and `image->elf_load_addr`.

## Risks And Edge Cases
Command-line length checking must include the added `elfcorehdr` prefix. Purgatory setup assumes the first word of `purgatory_start` is the master entry and must be preserved while replacing slave code.

## Test Signals
Kdump command-line tests for boundary lengths and purgatory symbol inspection after `kexec_file_load` provide coverage. End-to-end file-based kexec verifies the kernel and FDT addresses reach purgatory.
