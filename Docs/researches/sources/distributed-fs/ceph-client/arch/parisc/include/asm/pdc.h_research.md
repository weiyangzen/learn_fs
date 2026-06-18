# sources/distributed-fs/ceph-client/arch/parisc/include/asm/pdc.h

Purpose: defines core PA-RISC Processor Dependent Code firmware interface constants, status codes, structures, and call declarations.

Important APIs/types/functions: exports PDC procedure numbers, return codes, model/cache/BTLB/IO descriptors, and firmware helper prototypes used for console, inventory, cache, and boot services.

Control flow: early boot and platform code issue PDC calls with function/subfunction selectors, parse returned structures, and use the data to initialize CPU, memory, console, and devices.

State and persistence: firmware data persists in boot-time kernel structures; firmware itself owns platform state. Dependencies and integration: used by boot/compressed firmware code, processor setup, cache probing, device inventory, and PALO boot interactions.

Risks and test signals: structure layout and calling ABI are firmware contracts. Test on multiple PA-RISC firmware revisions, validate boot logs, and compare PDC-reported model/cache/device data.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
