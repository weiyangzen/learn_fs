# sources/distributed-fs/coda/coda-src/al/altest.c

Purpose: Interactive test and diagnostic program for the AL package. It lets an operator exercise name/ID translation, ACL allocation, external/internal conversion, CPS retrieval, byte-order conversion, rights checks, and membership checks.

Important APIs/functions: `ReadConfigFile`, `main`, `Op_1` through `Op_6`, `AskSlot`, `NewSlot`, and `GetInputOutput`. It manipulates four slot vectors for internal ACLs, external ACL strings, internal CPS objects, and external CPS strings.

Control flow: Startup reads `server.conf`, initializes vice paths, parses optional `-x` debug level, calls `AL_Initialize`, then loops over major operation menus. Each operation submenu prompts with `scanf`, allocates a slot, fills or converts structures, calls the relevant AL API, and prints results. `GetInputOutput` can redirect operation input from a file while suppressing prompts to `/dev/null`.

State and persistence: Maintains in-process `Vec[SLOTTYPES][SLOTMAX]` ownership flags and pointers. It does not directly mutate the PDB, but name translation and CPS retrieval read the configured protection database through AL/PDB. Debug level mutates the external `AL_DebugLevel`.

Dependencies and integration: Pulls in `prs.h`, `al.h`, `codaconf`, and `vice_file` for configuration. It is a developer/operator harness rather than production code.

Risks and test signals: The program uses unbounded `%s` into fixed buffers and assumes well-formed interactive input, so it should not be exposed to untrusted streams. The slot model is useful for manual regression testing but is not automated; failures are mostly printed rather than asserted.
