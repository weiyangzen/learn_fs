# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_multiple_domain_variants.h

## Purpose

`scoped_multiple_domain_variants.h` defines the three-process domain matrices used to test scoped access across parent, child, and grandchild processes. It distinguishes actual scope sandboxes from unrelated Landlock domains so tests can prove only scoped domains affect scoped resources.

## Important APIs, Types, and Functions

The header defines `enum sandbox_type` with `NO_SANDBOX`, `SCOPE_SANDBOX`, and `OTHER_SANDBOX`, then defines `FIXTURE_VARIANT(scoped_vs_unscoped)` with `domain_all`, `domain_parent`, `domain_children`, `domain_child`, and `domain_grand_child`. Seven variants encode allow/deny diagrams such as `deny_scoped`, `all_scoped`, `allow_with_other_domain`, and `deny_with_self_and_grandparent_domain`.

## Control Flow and State

There is no standalone execution. Consuming tests use each field to decide whether to create a scope ruleset, a filesystem-only domain, or no domain before/after forks. The resulting ancestry state determines whether a grandchild may reach child or parent sockets.

## Dependencies and Integration Points

It must be included by a test that declares `FIXTURE(scoped_vs_unscoped)` and supplies functions for scope and other-domain creation.

## Risks and Test Signals

Risks include conflating `OTHER_SANDBOX` with scope enforcement or misplacing domain creation before the wrong fork. Downstream test signals are matching P3-to-P2 and P3-to-P1 allow/deny outcomes for abstract UNIX socket operations.
