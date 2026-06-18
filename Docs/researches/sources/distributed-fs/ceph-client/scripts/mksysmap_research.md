<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mksysmap -->
# sources/distributed-fs/ceph-client/scripts/mksysmap

## Purpose

`mksysmap` is a sed filter that removes symbols unsuitable for `System.map` and kallsyms from sorted `nm -n` output.

## Important APIs, Types, and Functions

The file is itself a sed script. Rules delete local absolute/debug/undefined/local-weak symbols, local-label prefixes such as `$` and `.L`, and architecture-specific private namespaces such as arm64 EFI, PIE, and non-VHE KVM local symbols.

## Control Flow

Input lines are streamed through ordered sed delete patterns. Lines not matching any ignored symbol type or prefix pass through unchanged.

## State and Persistence Behavior

It is stateless and writes filtered symbols to stdout.

## Dependencies and Integration Points

It depends on sed and the symbol format produced by `nm -n`. It integrates with kernel `System.map` generation, kallsyms, module-init tools, and debugging tools.

## Risks and Edge Cases

Filtering is string-pattern based. New compiler-generated local symbol names or architecture namespaces can leak into `System.map` until a rule is added, while overly broad patterns can hide useful symbols. Format drift in `nm` output would break matching.

## Test Signals

Feed synthetic `nm` rows for ignored types, local labels, architecture prefixes, and normal exported/text/data symbols. Compare `System.map` content across architectures after compiler upgrades.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mksysmap -->
