# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/sutil.c

Purpose: Windows install/uninstall utility functions for network provider order and system environment variables, especially PATH.

Important APIs/types/functions: exported `InNetworkProviderOrder()`, `AddToProviderOrder()`, `RemoveFromProviderOrder()`, `ReadSystemEnv()`, `WriteSystemEnv()`, `AddToSystemPath()`, `RemoveFromSystemPath()`, and `IsWinNT()`. Private helpers read/write registry environment values on NT, read/write `c:\autoexec.bat` on Win9x, and perform case-insensitive substring search.

Control flow: provider-order operations open `HKLM...\NetworkProvider\Order`, read `ProviderOrder`, append or remove comma-separated entries, and write it back. Environment operations dispatch to registry or autoexec based on `GetVersion()`. PATH add/remove reads current `Path`, avoids duplicates with substring matching, appends with semicolon, or rebuilds a semicolon-separated list excluding the target.

State/persistence: persistent effects are registry updates to provider order and environment, or edits to `c:\autoexec.bat` via a temp file on Win9x. Allocated strings returned by read helpers must be freed by callers.

Dependencies/integration: depends on OpenAFS `afsreg` alternate registry helpers, Windows registry/filesystem APIs, and C runtime string/memory functions. Used by forced removal and setup utility code.

Risks/test signals: duplicate detection is substring-based, so a shorter path/provider token may match unintended entries. Buffer sizing for provider append allocates old length plus new length plus one comma byte but relies on null accounting from registry length. Tests should cover missing values, empty PATH, case-insensitive exact segment removal, substring false positives, NT vs Win9x dispatch, and autoexec temp-copy failure.
