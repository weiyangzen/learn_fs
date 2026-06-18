# sources/distributed-fs/eos/mgm/groupbalancer/ConverterUtils.hh

## Purpose
Declares transfer-name helpers and file skip filters used by both group balancing and group draining code paths.

## Important APIs, types, and functions
`SkipFileFn` is a `std::function<bool(std::string_view)>` predicate. `NullFilter` is an empty function meaning no filtering. `PrefixFilter` stores a prefix and implements path-prefix rejection. `getFileProcTransferNameAndSize()` is the exported helper that maps an EOS file id and target group to a converter proc-file name while returning the source file size.

## Control flow
Callers construct a filter appropriate to the workflow, invoke the helper, check for an empty result, then append workflow-specific tags such as `^groupbalancer^` or `^groupdrainer^` before scheduling a converter job.

## State and persistence
The header defines no persistent state. `PrefixFilter::prefix` is per-instance transient state.

## Dependencies and integration points
Includes `common/FileId.hh` and is consumed by `GroupBalancer.hh`, `GroupDrainer.cc`, and the implementation file. It is part of the converter scheduling boundary.

## Risks and test signals
Because `NullFilter` is an empty `std::function`, implementation code must guard it before invocation. Tests should validate filter construction from string views, empty filters, target group propagation, and compatibility with converter tag parsing.
