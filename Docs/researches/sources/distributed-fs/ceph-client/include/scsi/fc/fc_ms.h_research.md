# sources/distributed-fs/ceph-client/include/scsi/fc/fc_ms.h

Purpose: Defines Fibre Channel Management Service FDMI request codes, attribute identifiers/lengths, and packed request payloads for registering HBA and port attributes.

Important APIs/types/functions: Enums cover FDMI requests and HBA/port attribute types. Length macros document fixed attribute sizes. Structures include HBA identifiers, port names, variable-length attribute entries, attribute lists, registered port lists, RHBA/RHAT/RPRT/RPA, and deregistration payloads.

Control flow and state: No runtime logic is present. libfc builds these packed payloads during FDMI registration/deregistration against the management server.

Dependencies and integration: Depends on Linux types and FC-GS management service conventions. Integrated from libfc local-port states such as RHBA, RPA, DHBA, and DPRT.

Risks and test signals: Risks include variable-length attribute packing errors, wrong attribute length constants, unaligned big-endian fields, and incomplete deregistration payloads. Tests should validate FDMI request buffers, attribute count/length calculations, and management-server interop.
