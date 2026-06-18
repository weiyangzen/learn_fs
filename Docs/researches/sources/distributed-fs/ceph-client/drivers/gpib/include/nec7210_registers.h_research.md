# sources/distributed-fs/ceph-client/drivers/gpib/include/nec7210_registers.h

## Purpose

`nec7210_registers.h` defines chipset IDs, register numbers, register bit fields, auxiliary register values, and auxiliary commands for NEC7210-compatible GPIB controller chips.

## Important APIs and Constants

- `enum nec7210_chipset` identifies original NEC7210 and compatible/extended chips such as TNT4882, NAT4882, CB7210, IOT7210, IGPIB7210, and TNT5004.
- Write-register numbers include `CDOR`, `IMR1`, `IMR2`, `SPMR`, `ADMR`, `AUXMR`, `ADR`, and `EOSR`.
- Read-register numbers include `DIR`, `ISR1`, `ISR2`, `SPSR`, `ADSR`, `CPTR`, `ADR0`, and `ADR1`.
- Bit enums cover ISR/IMR data-in/out, errors, device clear, END, command pass-through, address changes, remote/local/lockout, serial request, address status, address mode, address register, serial poll, EOS/handshake modes, and parallel-poll modes.
- `enum aux_cmds` names controller commands such as chip reset, finish handshake, trigger, return to local, send EOI, go to standby, take control, listen/unlisten, execute parallel poll, IFC/REN controls, and secondary-address validation.

## Control Flow and Integration

The NEC7210 core uses these constants for every register read/write and interrupt decode. Board-specific extensions such as INES use base constants plus their own extra register bits.

## State and Persistence Behavior

No state is declared. Constants define the hardware state that `struct nec7210_priv` shadows and updates.

## Dependencies

The header is self-contained except for the include guard. It is consumed by `nec7210.h` and implementation files.

## Risks and Test Signals

Shared enum member names such as `IMR1`, `ADSR`, or `HR_END` can conflict if multiple controller register headers are included into one translation unit without care. Test signals are hardware register programming review, interrupt bit decoding, AUX command behavior, EOS/handshake mode transitions, and supported-chip compatibility.
