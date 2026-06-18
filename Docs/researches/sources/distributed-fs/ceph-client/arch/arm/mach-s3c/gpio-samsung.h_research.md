# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-samsung.h

Purpose: umbrella include for Samsung GPIO definitions.

Important APIs/types/functions: includes or exposes the platform-specific Samsung GPIO numbering/config declarations used by board code.

Control flow: no executable flow.

State and persistence: none directly.

Dependencies and integration points: used by S3C board headers and device setup to get GPIO constants and config APIs.

Risks: tiny forwarding header can mask include-order problems; changes affect many legacy board files.

Test signals: compile coverage for board files including this header.
