# sources/distributed-fs/openafs/src/bubasics/butm.p.h

`butm.p.h` is the private template for the generated public `butm.h` tape module interface. It defines tape block layout, tape operation vtables, tape state/config structures, tape status/flag bits, tape labels, naming macros, and vtable call macros.

Important types include `struct blockMark`, `struct butm_tapeInfo` with its `ops` function pointers, `struct tapeConfig`, and `struct butm_tapeLabel`. Constants define 16 KiB physical tape blocks, header/data sizes, tape status bits (`OFFLINE`, `TAPEERROR`, `EOF`, `EOD`), and flags (`READONLY`, `SEQUENTIAL`). Macros include `TNAME`, `TAPENAME`, `LABELNAME`, and `butm_*` dispatch wrappers.

There is no direct control flow; runtime dispatch happens through the function pointers in `butm_tapeInfo`. State includes tape position, byte/KByte/record/file counters, capacity model coefficients, mounted tape name, read-only/sequential flags, module-private rocks, error code, label metadata, expiration, dump id, use count, size, and dump path.

Dependencies are `afs/auth.h`, `afs/bubasics.h`, generated error table inclusion in the final header, and implementations that populate the ops table. Risks include ABI compatibility of function pointers, fixed-size label fields, macro buffer assumptions, a suspicious `butm_remainingSpace` reference to `(i)->Bytes` even though the structure defines `nBytes`, and unit ambiguity across historical version flags. Test signals are compile checks of generated `butm.h`, tape-module vtable conformance, label round trips, and capacity accounting tests.
