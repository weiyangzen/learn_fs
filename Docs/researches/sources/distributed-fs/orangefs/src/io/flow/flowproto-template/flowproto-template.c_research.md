# sources/distributed-fs/orangefs/src/io/flow/flowproto-template/flowproto-template.c

Purpose: example/skeleton flow protocol implementation.

Important APIs/functions: declares `flowproto_template_ops`, init/finalize/getinfo/setinfo/post/find_serviceable/service. Initialize and finalize return success; other operations return `-ENOSYS`.

Integration: module build comments it out. Like dump-offsets, the ops initializer includes serviceable/service callbacks that are not present in the visible `flowproto_ops` definition, so it is documentation or legacy template rather than active code.

Risks/test signals: re-enabling as-is is likely a compile failure or struct initializer mismatch. If used as a template, update it to the current ops shape and state model. Test signal is simply that disabled template code should stay out of active builds unless modernized.
