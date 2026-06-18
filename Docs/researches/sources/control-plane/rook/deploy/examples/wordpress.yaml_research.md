# sources/control-plane/rook/deploy/examples/wordpress.yaml

Purpose: provides the WordPress frontend half of the Rook-backed MySQL/WordPress sample.

Important APIs/types/functions: `Service/wordpress` type `LoadBalancer`, `PersistentVolumeClaim/wp-pv-claim`, and `Deployment/wordpress` using image `wordpress:4.6.1-apache`.

Control flow: the deployment mounts the PVC for WordPress content and connects to MySQL service from `mysql.yaml`.

State and persistence: WordPress files persist in `wp-pv-claim`; database state persists in the MySQL PVC.

Dependencies/integration: requires the MySQL example and a Rook-backed storage class.

Risks: old application image and example credentials are not production hardening.

Test signals: PVC bound, service gets external address, and WordPress install page can connect to MySQL.
