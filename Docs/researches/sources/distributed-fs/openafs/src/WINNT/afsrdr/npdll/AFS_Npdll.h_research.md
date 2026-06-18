# sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/AFS_Npdll.h

## Purpose

`sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/AFS_Npdll.h` is the small public-local header for the OpenAFS network-provider DLL. The complete 35-line file was read; it contains license text and the declaration needed by other translation units to force or share provider-name initialization.

## Important APIs, Types, and Functions

The only declaration is `void ReadProviderNameString(void);`. There are no local types, macros, or constants beyond the license/comment block.

## Control Flow

The header has no executable flow. Consumers include it to call the provider-name registry loader implemented in `AFS_Npdll.c`.

## State and Persistence Behavior

No state is defined in this header. The declared function affects `AFS_Npdll.c` static cached state by reading the provider name from the Windows registry.

## Dependencies and Integration Points

The integration point is `AFS_Npdll.c`, where `ReadProviderNameString` populates `wszProviderName` and `cbProviderNameLength` for `NETRESOURCE.lpProvider` values returned by enumeration and resource information calls.

## Risks and Edge Cases

The header intentionally exposes only one function, so the main risk is declaration drift if the implementation signature changes. Because it has no include guard, duplicate inclusion is harmless for the single function prototype but would become risky if definitions were later added.

## Test Signals

Compile coverage of the network-provider DLL is the primary signal. Runtime provider-name tests belong to `AFS_Npdll.c` because that file owns the registry read and cached data.
