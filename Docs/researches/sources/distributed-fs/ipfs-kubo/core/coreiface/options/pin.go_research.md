# sources/distributed-fs/ipfs-kubo/core/coreiface/options/pin.go

## Purpose
Builds settings for pin add, list, status, remove, and update operations.

## Important APIs, Types, and Functions
Defines `PinAddSettings`, `PinLsSettings`, `PinIsPinnedSettings`, `PinRmSettings`, `PinUpdateSettings`, option types, settings builders, `Pin` namespace, nested `Ls`/`IsPinned` namespaces, type filters, `Detailed`, `Name`, `Recursive`, `RmRecursive`, and `Unpin`.

## Control Flow and State
Defaults are recursive add/remove, list all, is-pinned all, update unpins old target. Type methods validate allowed pin types and return option functions. Detailed listing controls whether pin names are populated.

## Dependencies and Integration Points
Depends only on fmt. Consumed by PinAPI implementations and conformance tests around recursive/direct/indirect pin state.

## Risks and Test Signals
Risks include invalid type strings, precedence between recursive/direct/indirect pins, preserving pin names on update, and detailed-vs-nondetailed name exposure. Tests cover pin add/rm/list/is-pinned/verify, precedence, indirect listing, and names.
