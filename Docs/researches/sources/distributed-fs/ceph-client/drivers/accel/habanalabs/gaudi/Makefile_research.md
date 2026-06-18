# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/Makefile

Purpose: defines the Gaudi ASIC-specific object files that are included in the Habanalabs driver build.

Important APIs/types/functions: declares `HL_GAUDI_FILES := gaudi/gaudi.o gaudi/gaudi_security.o gaudi/gaudi_coresight.o`. There are no runtime functions in this Makefile.

Control flow: the parent Kbuild logic consumes `HL_GAUDI_FILES` so Gaudi device support, Gaudi security/protection setup, and Gaudi CoreSight support are linked when the driver is built with Gaudi support.

State and persistence behavior: no runtime state or persistence; this is build metadata only.

Dependencies and integration points: depends on neighboring Gaudi source files and the parent Habanalabs Kbuild composition. It integrates ASIC-specific Gaudi code with the common driver core, including the common security helper layer researched in this subset.

Risks and test signals: risks are build breakage or missing runtime support if object names drift or a needed object is omitted. Test signals are Habanalabs module builds with Gaudi enabled and symbol availability for Gaudi security and CoreSight initialization paths.
