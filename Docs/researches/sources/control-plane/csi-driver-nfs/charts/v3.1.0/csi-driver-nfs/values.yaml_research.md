# sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/values.yaml

Purpose: Default values for v3.1.0 chart.

Important APIs/types/functions: Image tags, serviceAccount/RBAC names, driver name and `mountPermissions`, feature flags for FSGroup and inline volume, controller working mount directory, node/controller resources and tolerations, imagePullSecrets.

Control flow: Templates consume values to render names, images, resources, driver capabilities, mount permissions, and controller working directory.

State and persistence: Values become Helm release configuration and rendered workload/RBAC objects.

Dependencies and integration points: Bridges chart settings to NFS driver flags and Kubernetes CSIDriver capability fields.

Risks: `mountPermissions: 0777` is permissive and may be parsed differently by YAML tooling if not handled consistently. Test signals: render values into driver args and validate created volume permissions.
