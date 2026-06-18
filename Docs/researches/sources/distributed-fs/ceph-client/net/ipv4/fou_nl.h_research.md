# sources/distributed-fs/ceph-client/net/ipv4/fou_nl.h

## Purpose
`fou_nl.h` is the generated kernel header for FOU generic-netlink glue. It shares policy/operation declarations and handler prototypes between generated netlink code and the FOU core implementation.

## Important APIs, Types, And Functions
The header declares `extern const struct nla_policy fou_nl_policy[FOU_ATTR_IFINDEX + 1]`, `extern const struct genl_small_ops fou_nl_ops[3]`, and the four handlers implemented in `fou_core.c`: `fou_nl_add_doit`, `fou_nl_del_doit`, `fou_nl_get_doit`, and `fou_nl_get_dumpit`.

## Control Flow
There is no executable control flow. Inclusion by `fou_nl.c` and `fou_core.c` allows the generated ops table to reference handlers while the core family registration references generated policy and ops.

## State And Persistence
The header owns no state. It contributes compile-time declarations only.

## Dependencies And Integration Points
It includes netlink/genetlink headers and UAPI `linux/fou.h`. Its generated-source comment ties it to `Documentation/netlink/specs/fou.yaml` and `tools/net/ynl/ynl-regen.sh`.

## Risks
Prototype drift between generated header and core handlers will break builds. Array size drift for ops or policy would desynchronize family registration. Since the file is generated, local manual patches are likely to be overwritten.

## Test Signals
Build coverage is the primary signal. Also verify YNL regeneration, module load, family registration, and that generated declarations match `fou_core.c` symbols.
