## sources/cloud-native/moby/daemon/internal/layer/ro_layer_windows.go

Purpose: Adds Windows-only descriptor exposure for read-only layers.

Important API: The file asserts `*roLayer` implements `distribution.Describable` and defines `Descriptor() distribution.Descriptor`.

Control flow and state: Returns the descriptor stored on the layer. No extra persistence; descriptor data is loaded/stored through file metadata.

Dependencies and integration: Lets Windows layer store layers expose distribution metadata to tar export/save paths and other distribution-aware code.

Risks: Empty descriptors are valid and mean no descriptor was stored. No direct tests in this subset.
