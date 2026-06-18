<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_history_opts.go -->
# sources/cloud-native/moby/client/image_history_opts.go

Purpose: declares functional option plumbing and result type for image history.

Important APIs/types/functions: `ImageHistoryOption`, private `imageHistoryOptionFunc`, `imageHistoryOpts`, `imageHistoryOptions`, and `ImageHistoryResult`.

Control flow: option funcs implement `Apply` to mutate private options. The result holds the decoded history item slice.

State and integration behavior: no persistence. The type structure lets `ImageHistory` evolve with additional options while preserving variadic call syntax.

Dependencies and risks: depends on image API history item types and OCI platform. Risks include duplicate option conflicts and public/private option struct drift.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_history_opts.go -->
