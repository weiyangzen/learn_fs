# File Research: sources/block-storage/lvm2/lib/report/columns-cmdlog.h

This header defines report columns for command log reporting through repeated `FIELD(...)` macro invocations.

Columns:
- `log_seq_num`: numeric sequence.
- `log_type`: log type.
- `log_context`: current context.
- `log_object_type`: current object type.
- `log_object_name`: current object name.
- `log_object_id`: current object ID.
- `log_object_group`: current object group.
- `log_object_group_id`: current object group ID.
- `log_message`: log message.
- `log_errno`: signed errno.
- `log_ret_code`: signed return code.

Role:
- Included by report/property generation code with `FIELD` defined by the includer.

Risks:
- This is not standalone C; include context must define `FIELD`, type identifiers such as `CMDLOG`, and display helpers.
