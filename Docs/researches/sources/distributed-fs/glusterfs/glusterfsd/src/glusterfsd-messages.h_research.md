# sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd-messages.h

Purpose: Central message-ID registry and message string definitions for the `GLUSTERFSD` logging component.

Important APIs and constants: Uses `GLFS_MSGID(GLUSTERFSD, ...)` to declare stable message IDs, then maps symbolic IDs like `glusterfsd_msg_1_STR` through `glusterfsd_msg_43_STR` and compatibility IDs `glusterfsd_msg_029_STR`, `glusterfsd_msg_041_STR`, and `glusterfsd_msg_042_STR` to log text.

Control flow: No runtime control flow; logging macros in daemon C files reference these symbols. The header comments define the governance rule: append new IDs, never delete IDs, and keep the component name aligned with `glfs-message-id.h`.

State and persistence: No state. The persistent contract is log/message ID stability for operators, documentation, and tooling.

Dependencies and integration: Depends on `<glusterfs/glfs-message-id.h>`. Integrated across `glusterfsd.c` and `glusterfsd-mgmt.c` via `gf_smsg`/`gf_msg` calls.

Risks: Reusing/removing IDs breaks log consumers and support tooling. Some message strings contain spelling mistakes preserved for compatibility, so cleanup edits may be externally visible. The out-of-order defines are intentional but easy to mishandle.

Test signals: Compile/link catches missing IDs. Operational log tests or message catalog checks are needed to catch accidental ID reuse or changed strings.
