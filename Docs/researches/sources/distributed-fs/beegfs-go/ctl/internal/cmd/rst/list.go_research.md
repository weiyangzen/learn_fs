# sources/distributed-fs/beegfs-go/ctl/internal/cmd/rst/list.go

Purpose: implements the `beegfs remote list` Cobra command for listing configured Remote Storage Targets and their user-visible configuration.

Important APIs/types/functions: `newListCmd` defines the CLI and `--show-secrets`; `runListCmd` retrieves RST config through `ctl/pkg/ctl/rst.GetRSTConfig`, sorts targets by ID, masks secrets by default, and renders `id`, `name`, `policies`, `type`, and `configuration` columns.

Control flow: command validates no positional args, calls the backend, sorts `response.Rsts`, skips the internal job-builder target, inspects `rst.WhichType`, and for S3 reflects protobuf fields to build a compact configuration string. Unknown types are hidden unless `--show-secrets` is set.

State and persistence: read-only. It surfaces persisted BeeRemote/RST configuration but does not modify it. Secret masking is front-end only.

Dependencies and integration points: integrates Cobra, `cmdfmt.NewPrintomatic`, common `rst.JobBuilderRstId`, Flex protobuf reflection, and the RST backend package.

Risks: the S3 configuration builder slices `stringBuilder.String()[:Len()-2]`; if an S3 message has no reflected fields this would panic. Reflection order is protobuf-defined but may not be ideal for stable human output. `--show-secrets` exposes secret material in stdout/table/JSON output.

Test signals: no direct tests. Important test cases would include S3 with/without secret masking, empty S3 config, unknown target types, sort order, and skipping the job-builder RST.
