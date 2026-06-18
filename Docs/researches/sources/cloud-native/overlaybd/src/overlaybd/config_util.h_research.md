<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/config_util.h -->
# sources/cloud-native/overlaybd/src/overlaybd/config_util.h

## Purpose
Provides a RapidJSON-based configuration wrapper and template accessors for typed JSON pointer reads and recursive merging.

## Important APIs, Types, And Functions
Defines aliases for RapidJSON `Document`, `Value`, arrays/objects, enum `FORMAT`, class `Config`, `is_vector`, overloaded `GetResult`, and macros `APPCFG_CLASS` and `APPCFG_PARA`.

## Control Flow
`Config` can parse JSON files or strings, pretty-print itself, and merge another JSON value recursively: object-object conflicts merge recursively, otherwise the right-hand value replaces the left. `GetResult` overloads return scalar values, document subtrees, scalar vectors, or document vectors by RapidJSON pointer path.

## State And Persistence
Reads configuration from files or strings into RapidJSON DOM state. Does not write files; `DumpString` serializes to memory.

## Dependencies And Integration Points
Depends on RapidJSON file streams/pointers/writers and Photon logging/DEFER utility. Macros support application config classes that expose typed getters.

## Risks And Test Signals
Constructor accepts `FORMAT` but always calls `ParseJSON`, so YAML/INI are not implemented. Scalar `GetResult` assumes RapidJSON type matches `T`; mismatches can assert. Vector overloads assume path exists and is an array. Source size reviewed: 185 lines; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/config_util.h -->
