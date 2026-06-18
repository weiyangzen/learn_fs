# sources/cloud-native/ostree/src/libostree/ostree-rollsum.h

Purpose: private header for rollsum match computation, defining the result container and cleanup API used by the implementation and tests.

Important APIs/types/functions: `OstreeRollsumMatches` stores source/target rollsum tables, CRC and byte-match counters, total destination chunks, aggregate matched bytes, and ordered match tuples. `_ostree_compute_rollsum_matches` computes results for two `GBytes` inputs. `_ostree_rollsum_matches_free` releases a result. `G_DEFINE_AUTOPTR_CLEANUP_FUNC` enables autoptr cleanup.

Control flow: callers pass immutable byte blobs, receive an owned result with owned GLib containers, inspect counters and match tuples, then free through the cleanup function.

State/persistence: no persistent state. The struct exposes internal containers directly, so in-tree consumers can observe or mutate the result.

Dependencies/integration: depends on libglnx, GIO/GLib, and `ostree-rollsum.c`. Tests include this header directly. It is not marked `_OSTREE_PUBLIC`, so it is internal.

Risks: the struct is not opaque, making representation visible to consumers. Match tuple formats are not named in the type system, so callers must know the `(utt)` and `(uttt)` conventions.

Test signals: direct test programs listed in `Makefile-tests.am` compile against this header and validate basic API linkage and behavior.
