<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_rename.go -->
# sources/cloud-native/moby/client/container_rename.go

Purpose: renames a container.

Important APIs/types/functions: `ContainerRenameOptions{Name string}`, `ContainerRenameResult`, and `Client.ContainerRename`.

Control flow: validates container id, sets `name=<Name>` query value, posts to `/containers/{id}/rename`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon mutates container metadata. Depends on shared `post` and id validation.

Risks and test signals: risk is missing name query or path drift. `container_rename_test.go` covers daemon errors, invalid ids, and successful route/query behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_rename.go -->
