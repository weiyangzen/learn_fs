# sources/distributed-fs/eos/mgm/utils/AttrHelper.hh

## Purpose
Declares attribute helper functions and a templated typed xattr getter for MGM code.

## Important APIs, types, and functions
The namespace `eos::mgm::attr` exposes `checkDirOwner()`, `checkAtomicUpload()`, `getVersioning()`, string `getValue()`, and arithmetic-template `getValue<T>()` enabled only for arithmetic types.

## Control flow
Callers pass an `IContainerMD::XAttrMap`; helpers apply policy-specific precedence. The numeric `getValue()` template finds a key and delegates conversion to `common::StringToNumeric()`.

## State and persistence behavior
Header-only template state is local to callers. No persistence occurs.

## Dependencies and integration points
Depends on namespace container metadata, `VirtualIdentity`, `StringUtils`, and C++ type traits. The functions are part of request attribute handling.

## Risks and test signals
Template conversion behavior depends on `StringToNumeric()` return semantics and target type bounds. Tests should verify signed/unsigned conversions, missing keys, invalid strings, and that non-arithmetic overloads are not selected.
