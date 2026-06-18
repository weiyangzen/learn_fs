<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ppc44x_simple.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ppc44x_simple.c

Purpose: provides a generic machine descriptor for simple 44x evaluation boards whose differences are fully described by device tree and drivers.

Important APIs/types/functions: `ppc44x_device_probe()` probes PLB4/OPB/EBC/simple-bus children; `board[]` lists compatible strings accepted by the generic machine; `ppc44x_probe()` matches the current machine and enables PCI resource reassignment; `define_machine(ppc44x_simple)` installs UIC, reset, and progress callbacks.

Control flow: early probe iterates compatible strings and returns true on match. The device initcall registers platform devices for standard buses. Interrupts use UIC and reset uses the common PPC4xx DBCR reset path.

State and persistence: no local mutable state. Persistent effects are PCI flags, registered devices, and selected machine callbacks.

Dependencies and integration: depends on OF compatible matching, board DT completeness, UIC, generic PCI bridge code, PPC4xx reset, and udbg.

Risks and test signals: adding a board to `board[]` assumes no custom early setup is needed; `ibm,ebony` appears here despite a dedicated Ebony file, so configuration combinations should avoid ambiguous machine claims. Test all listed compatibles for correct machine selection, bus population, PCI enumeration, and reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ppc44x_simple.c -->
