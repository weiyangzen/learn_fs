# sources/distributed-fs/lustre-release/lnet/lnet/udsp.c

## Purpose
`udsp.c` implements LNet User Defined Selection Policies. UDSP rules let users bias LNet path selection by assigning priorities to local/remote networks and NIDs, or by building preferred local-NID and preferred-router lists for peer NIs. The file stores policies, applies them to existing constructs, applies them incrementally to new NIs/peer NIs/peer nets, and marshals policies to and from ioctl buffers.

## Important APIs, Types, And Functions
- `struct udsp_info` carries the current local NI, local net, peer NI, peer net, match/action descriptors, priority, action type, local/remote preference mode, and revert flag through callback-based application.
- Rule matching helpers include `lnet_udsp_expr_list_equal`, `lnet_udsp_nid_descr_equal`, `lnet_udsp_action_equal`, `lnet_udsp_equal`, `lnet_udsp_criteria_present`, and `lnet_udsp_is_net_rule`.
- Application helpers include `lnet_udsp_apply_rule_on_ni`, `lnet_udsp_apply_prio_rule_on_net`, `lnet_udsp_apply_rule_on_nis`, `lnet_udsp_apply_rule_on_lpni`, `lnet_udsp_apply_rule_on_lpn`, `lnet_udsp_apply_rule_on_lpnis`, `lnet_udsp_apply_rte_list_on_net`, `lnet_udsp_apply_rte_rule_on_nets`, and `lnet_udsp_apply_single_policy`.
- Public application entry points are `lnet_udsp_apply_policies`, `lnet_udsp_apply_policies_on_ni`, `lnet_udsp_apply_policies_on_net`, `lnet_udsp_apply_policies_on_lpni`, and `lnet_udsp_apply_policies_on_lpn`.
- Policy list management is handled by `lnet_udsp_get_policy`, `lnet_udsp_add_policy`, `lnet_udsp_del_policy`, `lnet_udsp_alloc`, `lnet_udsp_free`, and `lnet_udsp_destroy`.
- Introspection and serialization use `lnet_udsp_get_construct_info`, `lnet_get_udsp_size`, `lnet_udsp_marshal`, `lnet_udsp_demarshal_add`, `copy_nid_range`, `copy_ioc_udsp_descr`, `copy_exprs`, and `copy_range_info`.

## Control Flow
Policy application is organized around three callback classes: peer-side rules, NI priority rules, and router-on-net rules. `lnet_udsp_apply_policies_helper` applies one rule or all rules in reverse list order. Reverse order lets earlier list entries override later-applied state when priorities and preferred lists are reset/rebuilt.

`lnet_udsp_apply_single_policy` classifies a rule by which descriptors are present. Source plus destination means a NID-pair rule: matching destination peer NIs receive a preferred local-NID list built from the source descriptor. Destination plus router means a router rule: matching destination peer NIs receive a preferred-router list built from route gateways matching the router descriptor. Destination alone means remote peer priority. Source alone means local NI or local network priority. Router-on-net application can also add preferred routers to local nets.

Preferred-list rules clear existing preference lists once per matched construct before adding matched NIDs or gateway NIDs. Revert mode clears rather than re-adds policy-generated preferences, so deletion and destruction can undo effects. Priority rules use `-1` as the reverted/default priority and call local selection-priority setters for `lnet_net`, `lnet_ni`, `lnet_peer_net`, or `lnet_peer_ni`.

Adding a policy scans the current list for a semantically equal match. Equal criteria plus changed priority updates the existing priority in place for priority rules; exact duplicates return `-EALREADY`. Otherwise the new policy is inserted at the requested index or appended, and later indices are incremented. Deleting by nonnegative index removes one policy, applies it in revert mode, frees it, and decrements subsequent indices. Deleting with a negative index destroys all policies.

Marshalling computes the exact byte size of an ioctl policy plus three NID descriptors. Each descriptor includes a fixed header, optional net-number range, and address expressions/ranges. `lnet_udsp_marshal` requires the caller's bulk size to exactly match `lnet_get_udsp_size`, copies descriptors to user memory, and asserts the whole buffer was consumed. Demarshalling validates truncation at each step, verifies descriptor type tags (`SRC`, `DST`, `RTE`), allocates one contiguous backing block for descriptor expression lists/ranges, and then inserts the resulting policy.

## State And Persistence Behavior
Policies are transient kernel objects on `the_lnet.ln_udsp_list`, allocated from `lnet_udsp_cachep`. Descriptor expression memory is stored as one allocated block per descriptor and freed by remembering `ud_mem_size`. Applying policies mutates transient selection state on local nets/NIs and peer nets/NIs: priorities, preferred local NID lists, local-net preferred router lists, and peer-NI preferred router lists.

There is no file persistence here. Persistent policy intent must come from userspace configuration replay. The function `lnet_udsp_destroy(shutdown)` optionally skips revert during shutdown because all constructs are being torn down.

## Dependencies And Integration Points
`udsp.c` depends on `udsp.h`, LNet peer/net structures, `cfs_match_net`, `cfs_match_nid_net`, expression-list helpers, route lists in `the_lnet.ln_remote_nets_hash`, preference-list APIs implemented in peer/net code, and user-copy helpers. It is invoked from peer and net creation paths to apply existing policies incrementally, and from ioctl/control paths to add, delete, show, or reconstruct policy effects.

The selection algorithm described in the file header consumes the priorities and preferred lists that this file writes. Router rules integrate with `router.c` by scanning configured routes and matching gateway primary or constituent NIDs.

## Risks
- Some rule validation logs errors but returns success-like `0` for bad action combinations, which may make userspace think a malformed rule was harmlessly accepted or ignored.
- `lnet_udsp_add_policy` updates duplicate priority policies in place but does not itself reapply the changed priority; callers must ensure application happens after add/update.
- Preferred-list application deliberately drops the net lock while clearing/adding preference lists. The surrounding code relies on `ln_api_mutex` and helper locking to keep selection lists consistent.
- The descriptor type check prints shifted bytes in a way that may not display the expected tag clearly on all endian/order cases.
- `lnet_udsp_marshal` uses exact-size matching, so ABI changes in ioctl structures or descriptor sizing can produce `-ENOSPC` instead of partial output compatibility.
- Demarshalling allocates packed expression backing memory and stores list pointers into it; any future change to descriptor ownership must preserve that free model.

## Test Signals
Tests should cover source-priority, destination-priority, NID-pair preferred local NI, router preferred list, local-net preferred-router rules, insertion at index, duplicate/update behavior, deletion/revert behavior, shutdown destroy without revert, marshalling/demarshalling round trips, truncated user buffers, invalid descriptor tags, and applying policies to constructs created after policies already exist.
