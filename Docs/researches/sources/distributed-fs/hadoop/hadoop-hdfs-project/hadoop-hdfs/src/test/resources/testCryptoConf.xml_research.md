# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testCryptoConf.xml

## Purpose

`testCryptoConf.xml` is the HDFS crypto CLI test definition. The complete 738-line file was read. It defines 35 tests for encryption-zone command usage, encryption-zone creation errors and successes, rename restrictions across encryption zones, trash provisioning, file encryption info lookup, encryption-zone listing with Trash and snapshots, and re-encryption commands.

## Important APIs, Types, and Functions

The fixture uses `<crypto-admin-command>` entries and normal DFS shell commands. Crypto commands include usage/help, `-createZone -keyName ... -path ...`, `-provisionTrash -path ...`, `-getFileEncryptionInfo -path ...`, `-listZones`, `-reencryptZone -start`, `-reencryptZone -cancel`, and `-listReencryptionStatus`. DFS shell setup/cleanup commands include `-mkdir`, `-touchz`, `-ls`, `-mv`, `-rm`, `-rm -r`, `-rm -r -skipTrash`, `-rmdir`, `-allowSnapshot`, `-createSnapshot`, and `-deleteSnapshot`. Comparators include substring, regex-across-output, and token comparison.

## Control Flow

Early tests validate usage/help argument handling and create-zone errors for missing paths, duplicate zones, non-empty directories, missing keys, missing path, and missing key name. Creation success is checked for subdirectories and nested paths. Rename tests validate disallowed moves across zones, into zones, and from zones, while allowing encryption-zone root rename and intra-zone rename. Trash provisioning tests cover non-zone paths, pre-existing `.Trash`, successful provisioning, and incorrect subdirectory roots. File encryption info tests check EZ files, non-EZ files, nonexistent files, EZ directories, and subdirectories. Zone listing tests verify deleted zones remain listed under Trash, permanently deleted zones disappear, snapshots preserve deleted zones, and nested snapshot/trash scenarios behave correctly. Re-encryption tests cover successful submission, non-EZ rejection, cancel rejection for zones not being re-encrypted, and list status tokens.

## State and Persistence Behavior

The tests mutate encryption-zone xattrs/metadata, create `.Trash` under zones, move or delete paths into user Trash, create snapshots that preserve zone roots, and submit re-encryption state. Cleanup uses `-skipTrash` or explicit Trash cleanup where necessary so zone listing expectations are isolated.

## Dependencies and Integration Points

It integrates with the `CryptoAdmin` CLI, key provider setup for `myKey` and `zone2`, NameNode encryption-zone manager, DFS rename restrictions, Trash semantics, snapshot manager, file encryption info lookup, and re-encryption status tracking.

## Risks and Edge Cases

Risks include accidentally permitting cross-zone renames, failing to provision zone-local Trash, stale deleted zones in listings after permanent cleanup, snapshot references hiding deleted-zone metadata, key-existence errors changing text, and asynchronous re-encryption status output being too timing-sensitive for token comparison.

## Test Signals

Signals are expected usage/help/error strings, `Added encryption zone` success messages, rename denial messages naming source/destination zones, Trash provisioning messages, `keyName: myKey, ezKeyVersionName: myKey@0`, no-info and file-not-found errors, regex listing of live/Trash/snapshot zones, and `/src,Completed,false,myKey,zone2` token output for re-encryption status.
