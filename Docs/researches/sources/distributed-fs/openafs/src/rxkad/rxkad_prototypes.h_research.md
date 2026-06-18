# sources/distributed-fs/openafs/src/rxkad/rxkad_prototypes.h

Purpose: Declares the rxkad API surface across packet crypto, fcrypt, client/server security classes, common connection operations, ticket routines, CRC helpers, and Kerberos v5 support.

Important APIs: Prototypes include `rxkad_EncryptPacket`, `rxkad_DecryptPacket`, `fc_*`, `rxkad_NewClientSecurityObject`, `rxkad_GetResponse`, shared connection/packet/stats operations, `rxkad_NewServerSecurityObject`, `rxkad_NewKrb5ServerSecurityObject`, challenge processing, `rxkad_GetServerInfo`, `rxkad_SetConfiguration`, v4 ticket routines, v5 ticket routines, and `tkt_DeriveDesKey`.

Control flow and state: No runtime behavior, but this header establishes cross-file coupling and installed declarations.

Dependencies and integration: Included from `rxkad.p.h` after core typedefs are defined. It pulls in `fcrypt.h` and `rx/rx.h`.

Risks: Some legacy prototypes expose mutable char pointers and broad callback signatures. ABI compatibility constrains cleanup. The declared `rxkad_AllocCID` and `rxkad_ResetState` are historical declarations not implemented in this file group.

Test signals: All rxkad builds depend on prototype consistency; stress clients and servers exercise the public constructors and server-info APIs.
