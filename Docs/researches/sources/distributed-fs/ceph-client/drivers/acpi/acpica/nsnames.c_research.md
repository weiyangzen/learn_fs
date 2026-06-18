<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsnames.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsnames.c

## Purpose
Builds and normalizes namespace names and paths. It converts handles to simple names or full paths, constructs normalized absolute paths, combines scope prefixes with internal AML paths, and strips trailing underscores for display.

## Important APIs, Types, And Functions
Key routines are `acpi_ns_get_external_pathname`, `acpi_ns_get_pathname_length`, `acpi_ns_handle_to_name`, `acpi_ns_handle_to_pathname`, `acpi_ns_build_normalized_path`, `acpi_ns_get_normalized_pathname`, `acpi_ns_build_prefixed_pathname`, and `acpi_ns_normalize_pathname`.

## Control Flow
Handle helpers validate namespace handles, calculate required buffer sizes with `acpi_ns_build_normalized_path`, initialize caller buffers, then write names or full paths. Normalized path building walks from node to root, writes reversed name segments with optional trailing-underscore suppression and root prefix, reverses the assembled buffer, and appends NUL. Prefix building obtains the prefix scope path, externalizes the internal AML path, avoids prepending when the path is already absolute or parent-prefixed, normalizes display underscores, and concatenates. Pathname normalization copies special prefixes then removes trailing underscores from each segment in place via a temporary buffer.

## State And Persistence
No namespace state is mutated. The file allocates returned pathname buffers and initializes caller-provided buffers.

## Dependencies And Integration Points
Used by diagnostics, evaluation warnings, namespace dumping, and error reporting. Depends on handle validation, AML name externalization, ACPICA buffer initialization, and allocation utilities.

## Risks And Edge Cases
Path-size computation and write mode share one routine, so off-by-one errors would affect caller buffer contracts. `no_trailing` must not remove leading underscores. Prefix concatenation must preserve fully qualified and parent-prefixed paths. Invalid handles return bad-parameter statuses.

## Test Signals
Check root paths, deep paths, names with trailing underscores, leading underscore segments, parent/root-prefixed internal paths, too-small caller buffers, invalid handles, and allocated path freeing under leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsnames.c -->
