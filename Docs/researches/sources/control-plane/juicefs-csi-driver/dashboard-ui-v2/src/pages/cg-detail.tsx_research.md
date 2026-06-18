# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/cg-detail.tsx

## Purpose
`CgDetail` displays one JuiceFS CacheGroup and lets users edit or delete it.

## APIs, Control Flow, and State
It fetches a CacheGroup with `useCacheGroup`, tracks YAML modal visibility and worker auto-refresh, and renders namespace, phase, expected/ready workers, and cache group status. Editable YAML omits `metadata.managedFields`, saves through `useUpdateCacheGroup`, shows success/error messages, mutates the SWR cache, and enables worker auto-refresh. Delete calls `useDeleteCacheGroup` then navigates to `/cachegroups`.

## Dependencies and Integration Points
It composes `YamlModal`, `CgWorkersTable`, CacheGroup hooks, Ant Design notifications, `YAML.parse/stringify`, and router navigation.

## Risks and Test Signals
The update hook returns parsed JSON from `apiFetch`, but this component casts it to `Response` and checks `resp.status`, which may not work with the utility contract. Test YAML update success/failure, delete failure JSON parsing, and worker refresh after update.
