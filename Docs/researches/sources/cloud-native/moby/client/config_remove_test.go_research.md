<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_remove_test.go -->
# sources/cloud-native/moby/client/config_remove_test.go

Purpose: tests `ConfigRemove` invalid-id behavior, error propagation, and successful route construction.

Important coverage: empty and whitespace ids map to `cerrdefs.IsInvalidArgument`; daemon 500 maps to internal; success expects `DELETE /configs/config_id`.

Control flow and dependencies: uses package mock client helpers and gotest assertions.

State and risks: no persistent state. The test protects destructive route correctness for config removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_remove_test.go -->
