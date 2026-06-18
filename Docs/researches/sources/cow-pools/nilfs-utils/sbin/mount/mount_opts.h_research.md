# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_opts.h

## Scope

Declares legacy mount option flags and option string helper APIs.

## API Surface

- Defines user-space-only mount option bits such as `MS_NOAUTO`, `MS_USERS`, `MS_USER`, `MS_OWNER`, `MS_GROUP`, `MS_NETDEV`, `MS_COMMENT`, and `MS_LOOP`.
- Defines masks for options hidden from `mount(2)` or mtab, and secure defaults for user/owner mounts.
- Declares global option state expected from helper programs.
- Declares option append/parse/reconstruction helpers and NILFS-specific find/replace helpers.
- `replace_drop_opt()` macro replaces an option when a condition is true or removes it when false.

## Dependencies And Risks

The custom `MS_*` bits must not collide with real kernel flags used by the helper. Macro `replace_drop_opt()` evaluates arguments in a GNU statement expression and is not strictly ISO C.
