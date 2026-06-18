<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescoord.h -->
# sources/distributed-fs/coda/coda-src/resolution/rescoord.h

Purpose: public coordinator-side directory resolution declarations.

Important APIs: `IsWeaklyEqual` tests store-id equality for version vectors. `WEResPhase1` forces a new version vector and returns success host state/status. `CompareDirContents` compares fetched directory/ACL buffers. `RegDirResolution` resolves weak equality/runt/already-equal/already-inconsistent directory cases or reports that log resolution is required.

State/persistence: no state in the header. Implementations mutate remote replicas through `res_mgrpent` RPC handles and update resolution status.

Dependencies/integration: depends on `ViceFid`, `ViceVersionVector`, `res_mgrpent`, `ViceStoreId`, `ResStatus`, and `SE_Descriptor` definitions from included users. It is included by file and directory resolution modules.

Risks/test signals: forward declarations are implicit through other headers; direct inclusion may require prior type definitions. Test compilation units that include this header alone or adjust includes if modernizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescoord.h -->
