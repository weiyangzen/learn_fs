# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/fiq.S

Purpose: default RiscPC FIQ handler stub.

Important APIs/types/functions: defines `rpc_default_fiq_start` as the platform default FIQ entry.

Control flow: minimal assembly path for FIQ handling before another handler, such as floppy DMA, is installed.

State and persistence: affects CPU exception handling only through installed FIQ vector code.

Dependencies and integration points: linked by RiscPC FIQ setup and ARM FIQ framework.

Risks: a bad default FIQ path can lock the machine during unexpected fast interrupts.

Test signals: boot with no claimed FIQ users and floppy FIQ handler replacement/restoration.
