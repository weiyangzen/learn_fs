# sources/distributed-fs/ipfs-kubo/core/coreiface/options/object.go

## Purpose
Builds settings for object link addition/removal, including UnixFS validation bypass controls.

## Important APIs, Types, and Functions
Defines `ObjectAddLinkSettings`, `ObjectRmLinkSettings`, option types, `ObjectAddLinkOptions`, `ObjectRmLinkOptions`, `Object` namespace, and methods `Create`, `SkipUnixFSValidation`, and `RmLinkSkipUnixFSValidation`.

## Control Flow and State
Add-link defaults to no parent creation and validation enabled. Remove-link defaults to validation enabled. Options flip booleans; implementations enforce directory/HAMT/raw dag-pb safety unless bypassed.

## Dependencies and Integration Points
No external dependencies. Consumed by ObjectAPI and its conformance tests.

## Risks and Test Signals
Risks include exposing validation bypass too broadly and inconsistent add/remove bypass names. Tests explicitly cover UnixFS directory/file/HAMT/raw dag-pb validation and bypass behavior.
