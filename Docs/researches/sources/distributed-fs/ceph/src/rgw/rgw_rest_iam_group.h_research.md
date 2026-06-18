# sources/distributed-fs/ceph/src/rgw/rgw_rest_iam_group.h

## Purpose

`rgw_rest_iam_group.h` declares factory functions for IAM group-related `RGWOp` objects. It keeps concrete group operation classes private to the implementation while exposing constructors to the central IAM dispatcher.

## Important APIs

Factories cover group lifecycle, membership, groups-for-user listing, inline group policies, managed policy attach/detach, and attached policy listing: `make_iam_create_group_op()`, `make_iam_get_group_op()`, `make_iam_update_group_op()`, `make_iam_delete_group_op()`, `make_iam_list_groups_op()`, `make_iam_add_user_to_group_op()`, `make_iam_remove_user_from_group_op()`, `make_iam_list_groups_for_user_op()`, `make_iam_put_group_policy_op()`, `make_iam_get_group_policy_op()`, `make_iam_delete_group_policy_op()`, `make_iam_list_group_policies_op()`, `make_iam_attach_group_policy_op()`, `make_iam_detach_group_policy_op()`, and `make_iam_list_attached_group_policies_op()`.

## Control Flow and Integration

`rgw_rest_iam.cc` stores these function pointers in its `Action` map. Mutating factories accept the original POST body for multisite forwarding. Read-only factories ignore the body.

## Risks and Test Signals

The header is a dispatcher contract. Missing a factory in the action map makes a compiled operation unreachable; changing a signature breaks central IAM dispatch. Compile/link tests and action-dispatch tests should cover every declared factory.
