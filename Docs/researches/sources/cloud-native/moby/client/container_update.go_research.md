<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_update.go -->
# sources/cloud-native/moby/client/container_update.go

Purpose: updates container resource settings.

Important APIs/types/functions: `ContainerUpdateOptions` wrapping resource update configuration, `ContainerUpdateResult`, and `Client.ContainerUpdate`.

Control flow: validates container id, posts the update config as JSON to `/containers/{id}/update`, closes response, decodes daemon warnings when present, and returns them in the result.

State and integration behavior: no local persistence; daemon mutates container resource configuration. Depends on container API resource types and shared request helpers.

Risks and test signals: risks are body shape drift and warning decode loss. `container_update_test.go` covers internal errors, invalid ids, route, body/decode behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_update.go -->
