# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/cg-list.tsx

## Purpose
`CgList` lists CacheGroups and provides a YAML template flow to create one.

## APIs, Control Flow, and State
It fetches CacheGroups with `useCacheGroups`, defines columns for name, filesystem, phase, ready string, and creation time, and uses an editable `YamlModal` seeded with a default CacheGroup manifest. Saving parses YAML and calls `useCreateCacheGroup`, then mutates the list and closes the modal.

## Dependencies and Integration Points
It uses CacheGroup API hooks, Ant Design Pro table, `react-intl`, YAML parsing, and routes to `/cachegroups/:namespace/:name`.

## Risks and Test Signals
The template includes an EE mount image and host networking defaults that may not suit all clusters. Creation errors assume JSON-formatted error messages. Test malformed YAML, API validation errors, empty list, and successful mutate after create.
