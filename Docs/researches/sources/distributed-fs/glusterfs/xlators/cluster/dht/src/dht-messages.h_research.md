# Research: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-messages.h

## Purpose

`dht-messages.h` is the DHT translator's structured logging catalog. It declares the stable `DHT_MSG_*` message IDs through `GLFS_MSGID` and defines reusable string constants for many log messages. The file gives DHT code a common vocabulary for layout, lookup, migration, rebalance, lock, and memory failure reporting.

## Important APIs, Types, and Functions

The central macro invocation is `GLFS_MSGID(DHT, ...)`, which registers a long append-only list of message identifiers with the Gluster message ID system. The comments explicitly state the compatibility rule: append new IDs at the end, never delete or reuse old IDs, and keep the component name aligned with `glfs-message-id.h`.

The string macros cover common operational failures and status messages: subvolume selection failures, GFID mismatch or null GFID, invalid disk layout, directory self-heal and layout repair failures, migration start/complete/failure/skipped messages, hardlink migration failures, rebalance status, lock migration errors, lock/unlock failures, dictionary allocation and set failures, and namespace protection errors.

## Control Flow and Integration

There is no executable control flow, but the file is heavily integrated by calls to `gf_msg`, `gf_smsg`, `gf_log`, and debug logging throughout DHT. The researched `dht-lock.c` uses lock-specific IDs such as `DHT_MSG_LK_ARRAY_INFO`, `DHT_MSG_UNLOCKING_FAILED`, `DHT_MSG_INODELK_FAILED`, `DHT_MSG_ENTRYLK_FAILED_AFT_INODELK`, `DHT_MSG_BLOCK_INODELK_FAILED`, and allocation failure IDs. `dht-rebalance.c` uses many migration and rebalance IDs, including `DHT_MSG_MIGRATE_FILE_FAILED`, `DHT_MSG_MIGRATE_FILE_COMPLETE`, `DHT_MSG_MIGRATE_FILE_SKIPPED`, `DHT_MSG_REBALANCE_STATUS`, and `DHT_MSG_REBALANCE_STOPPED`.

## State and Persistence Behavior

Message IDs are source-level constants, but they behave like a persistent interface for logs, support tooling, and alert rules. Once emitted in field logs, ID stability matters. String macros are less rigid than IDs but still affect operator-facing diagnostics and tests that match log text.

## Dependencies and Constraints

The header depends on `<glusterfs/glfs-message-id.h>`. Message definitions must remain unique within the component. New logging sites should prefer existing IDs when semantics match and append IDs when a new failure class needs independent observability. Typos in existing strings are compatibility-sensitive because changing them may affect log consumers, even when the spelling is incorrect.

## Risks and Test Signals

The largest risk is accidental ID reuse or insertion in the middle of the macro list, which can change numeric assignments. Another risk is semantic overload, where unrelated failures reuse a broad ID and become hard to triage. Test signals include build success for all files including this header, structured log output carrying the expected DHT component IDs, and no duplicate or reordered message IDs in generated message catalogs.
